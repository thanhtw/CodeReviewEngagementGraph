import { generateAllLabelsGraph } from "./graph_func.js";
import { 
    generateRelevanceGraph,
    generateConcretenessGraph,
    generateConstructiveGraph,
    generateAllGraph,
} from './graph_3labelFunc.js';
// 簡化 import - 只保留需要的函數
// 注意：我們不再使用分析圖表功能，但保留 import 以避免錯誤



let currentMode = 'all';
let rawData = null;
let currentHW = []; // 將從JSON檔案動態載入
let bubbleChartManager = null; // 新增 Bubble Chart 管理器



export function updateGraphMode(mode, hwNames = [...currentHW]) {
    if (!rawData) return;
    currentMode = mode;
    currentHW = [...hwNames]; // 深拷貝以避免引用問題

    // 更新按鈕的 active 狀態
    console.log(`🔵 正在更新按鈕狀態，模式: ${mode}`);
    document.querySelectorAll('.switch-btn').forEach((btn, index) => {
        btn.classList.remove('active');
        console.log(`移除按鈕 ${index} 的 active 狀態`);
    });
    
    // 為當前模式的按鈕添加 active 類
    const modeButtons = {
        'all': 0,
        'relevance': 1,
        'concreteness': 2,
        'constructive': 3
    };
    
    const buttons = document.querySelectorAll('.switch-btn');
    const targetIndex = modeButtons[mode];
    console.log(`目標按鈕索引: ${targetIndex}，總按鈕數: ${buttons.length}`);
    
    if (buttons[targetIndex]) {
        buttons[targetIndex].classList.add('active');
        console.log(`✅ 為按鈕 ${targetIndex} 添加 active 狀態`);
    } else {
        console.error(`❌ 找不到索引 ${targetIndex} 的按鈕`);
    }

    switch(mode) {
        case 'all':
            console.log(`切換到All模式 (3個標籤score平均) (${hwNames.join(',')})`);
            generateAllGraph(rawData, hwNames);
            break;
        case 'relevance':
            console.log(`切換到relevance (${hwNames.join(',')})`);
            generateRelevanceGraph(rawData, hwNames);
            break;
        case 'concreteness':
            console.log(`切換到concreteness (${hwNames.join(',')})`);
            generateConcretenessGraph(rawData, hwNames);
            break;
        case 'constructive':
            console.log(`切換到constructive (${hwNames.join(',')})`);
            generateConstructiveGraph(rawData, hwNames);
            break;
    }
    updateBubbleChartOnly(hwNames); // 只更新氣泡圖，不處理分析圖表

}

window.updateGraphMode = updateGraphMode;

document.addEventListener("DOMContentLoaded", function () {
    // 初始化作業標籤圖表按鈕事件
    initHwLabelChartEvents();
    
    // 初始化 Bubble Chart
    if (window.BubbleChartManager) {
        bubbleChartManager = new window.BubbleChartManager();
    }
    
    fetch("../function/3labeled_processed_totalData.json")
        .then(response => response.json())
        .then(data => {
            rawData = data;
            
            // 動態生成作業選項
            const hwKeys = Object.keys(data).sort(); // 獲取並排序作業列表
            console.log("📋 從JSON檔案中發現的作業:", hwKeys);
            
            // 更新全域變數
            currentHW = [...hwKeys];
            
            // 動態生成select選項
            const hwSelect = document.getElementById('hw-select');
            if (hwSelect) {
                // 清空現有選項
                hwSelect.innerHTML = '';
                
                // 添加新選項
                hwKeys.forEach(hwKey => {
                    const option = document.createElement('option');
                    option.value = hwKey;
                    option.textContent = hwKey;
                    option.selected = true; // 預設全選
                    hwSelect.appendChild(option);
                });
                
                console.log(`✅ 已動態生成 ${hwKeys.length} 個作業選項`);
            }
            
            console.log("原始資料範例：", data.HW4?.[15]);
            updateGraphMode('all', currentHW); // 初始化時傳遞 currentHW
        })
        .catch(error => {
            console.error("讀取 JSON 失敗:", error);
        });
});


// GO 按鈕
document.getElementById('hw-apply-btn').addEventListener('click', () => {
    const select = document.getElementById('hw-select');
    const selectedHWs = Array.from(select.selectedOptions).map(opt => opt.value);
    if (selectedHWs.length === 0) {
        alert("請至少選擇一個作業！");
        return;
    }
    currentHW = [...selectedHWs];
    // 強制以當前模式重新生成圖表
    updateGraphMode(currentMode, currentHW);
});

// 只更新氣泡圖的簡化函數
function updateBubbleChartOnly(hwNames) {
    console.log("🫧 updateBubbleChartOnly 被呼叫", hwNames);
    if (!rawData || !bubbleChartManager) return;
    
    try {
        console.log("只更新氣泡圖", { hwNames });
        
        // 準備網絡圖資料給 Bubble Chart
        const networkData = prepareNetworkDataForBubbleChart(hwNames);
        if (networkData) {
            bubbleChartManager.updateData(networkData);
        }
    } catch (error) {
        console.error("更新氣泡圖時發生錯誤:", error);
    }
}

function updateAnalysisCharts(hwNames) {
    // 此函數已停用 - 不再處理分析圖表，因為HTML元素已被刪除
    console.log("⚠️ updateAnalysisCharts 被呼叫但已停用", hwNames);
    return;
}

// 為 Bubble Chart 準備網絡圖資料
function prepareNetworkDataForBubbleChart(hwNames) {
    if (!rawData) return null;

    const studentData = new Map();
    
    hwNames.forEach(hwName => {
        const hwData = rawData[hwName] || [];
        console.log(`處理 ${hwName}，共 ${hwData.length} 筆資料`);
        
        hwData.forEach(assignment => {
            const reviewer = assignment.Reviewer_Name || assignment.reviewer;
            const author = assignment.Author_Name || assignment.author;
            
            // 確保兩個學生都在資料中
            [reviewer, author].forEach(studentId => {
                if (studentId && !studentData.has(studentId)) {
                    studentData.set(studentId, {
                        id: studentId,
                        name: studentId,
                        validComments: 0,        // 完成審查的 Assignment 數（用於審查參與度計算）
                        validRounds: 0,          // 有效評論的 Round 數（用於標籤比例計算）
                        assignedTasks: 0,
                        relevanceCount: 0,
                        concretenessCount: 0,
                        constructiveCount: 0
                    });
                }
            });
            
            // 處理評論者（reviewer）資料
            if (reviewer && studentData.has(reviewer)) {
                const reviewerData = studentData.get(reviewer);
                reviewerData.assignedTasks++;
                
                // 檢查是否完成審查任務（有任何有效評論）
                let hasValidFeedback = false;  // 這個assignment是否有有效評論
                let validRoundsCount = 0;       // 這個assignment中有效Round的數量
                let relevanceCount = 0;
                let concretenessCount = 0;
                let constructiveCount = 0;
                
                if (assignment.Round && assignment.Round.length > 0) {
                    assignment.Round.forEach(round => {
                        // 檢查是否有有效評論內容
                        if (round.Feedback && round.Feedback.trim() !== "") {
                            hasValidFeedback = true;  // 標記這個assignment有有效評論
                            validRoundsCount++;       // 統計有效Round數量
                            
                            // 統計標籤
                            if (round.Relevance === 1) {
                                relevanceCount++;
                            }
                            if (round.Concreteness === 1) {
                                concretenessCount++;
                            }
                            if (round.Constructive === 1) {
                                constructiveCount++;
                            }
                        }
                    });
                }
                
                // 如果這個assignment有有效評論，則算作完成一個審查任務
                if (hasValidFeedback) {
                    reviewerData.validComments++;
                }
                
                // 累加有效Round數量（用於標籤比例計算）
                reviewerData.validRounds += validRoundsCount;
                
                reviewerData.relevanceCount += relevanceCount;
                reviewerData.concretenessCount += concretenessCount;
                reviewerData.constructiveCount += constructiveCount;
            }
        });
    });
    
    // 轉換為節點格式
    const nodes = Array.from(studentData.values()).map(student => ({
        id: student.id,
        label: student.name,
        group: 'student',
        validComments: student.validComments,    // 完成的 Assignment 數（用於審查參與度）
        validRounds: student.validRounds,        // 有效的 Round 數（用於標籤比例）
        assignedTasks: student.assignedTasks,
        relevanceCount: student.relevanceCount,
        concretenessCount: student.concretenessCount,
        constructiveCount: student.constructiveCount
    }));
    
    console.log(`Bubble Chart 準備完成：共 ${nodes.length} 位學生`);
    console.log('前5位學生資料:', nodes.slice(0, 5));
    
    return { nodes, edges: [] }; // Bubble Chart 只需要節點資料
}

// 初始化全作業標籤頻率圖表按鈕事件
function initHwLabelChartEvents() {
    console.log('開始初始化全作業標籤圖表按鈕事件...');
    
    // 所有評論的圖表按鈕
    const generateBtn = document.getElementById('generateHwChart');
    const downloadBtn = document.getElementById('downloadHwChart');
    
    // 僅有效評論的圖表按鈕
    const generateValidBtn = document.getElementById('generateHwValidChart');
    const downloadValidBtn = document.getElementById('downloadHwValidChart');
    
    console.log('按鈕元素檢查:', {
        generateBtn: !!generateBtn,
        downloadBtn: !!downloadBtn,
        generateValidBtn: !!generateValidBtn,
        downloadValidBtn: !!downloadValidBtn
    });
    
    let currentHwChart = null;
    let currentHwValidChart = null;
    
    // 所有評論圖表事件處理
    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            console.log('開始生成全作業標籤頻率圖表（所有評論）...');
            generateBtn.textContent = '生成中...';
            generateBtn.disabled = true;
            
            try {
                currentHwChart = await generateHwLabelChart();
                if (currentHwChart) {
                    console.log('圖表生成成功（所有評論）');
                    downloadBtn.disabled = false;
                }
            } catch (error) {
                console.error('生成圖表失敗:', error);
                alert('生成圖表失敗，請檢查控制台錯誤信息');
            } finally {
                generateBtn.textContent = '生成圖表（所有評論）';
                generateBtn.disabled = false;
            }
        });
    }
    
    if (downloadBtn) {
        downloadBtn.disabled = true;
        downloadBtn.addEventListener('click', () => {
            if (currentHwChart) {
                saveChartAsPNG(currentHwChart, 'hwLabelChart_all.png');
            } else {
                alert('請先生成圖表');
            }
        });
    }
    
    // 僅有效評論圖表事件處理
    if (generateValidBtn) {
        console.log('綁定僅有效評論圖表生成按鈕事件');
        generateValidBtn.addEventListener('click', async () => {
            console.log('點擊僅有效評論圖表生成按鈕');
            console.log('開始生成全作業標籤頻率圖表（僅有效評論）...');
            generateValidBtn.textContent = '生成中...';
            generateValidBtn.disabled = true;
            
            try {
                currentHwValidChart = await generateHwEnableLabelChart();
                if (currentHwValidChart) {
                    console.log('圖表生成成功（僅有效評論）');
                    downloadValidBtn.disabled = false;
                } else {
                    console.log('圖表生成失敗：返回null');
                }
            } catch (error) {
                console.error('生成圖表失敗:', error);
                alert('生成圖表失敗，請檢查控制台錯誤信息');
            } finally {
                generateValidBtn.textContent = '生成圖表（僅有標籤）';
                generateValidBtn.disabled = false;
            }
        });
    } else {
        console.log('警告: 找不到僅有效評論圖表生成按鈕');
    }
    
    if (downloadValidBtn) {
        downloadValidBtn.disabled = true;
        downloadValidBtn.addEventListener('click', () => {
            if (currentHwValidChart) {
                saveChartAsPNG(currentHwValidChart, 'hwLabelChart_valid.png');
            } else {
                alert('請先生成圖表');
            }
        });
    }
}

