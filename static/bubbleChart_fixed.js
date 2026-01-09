/**
 * Bubble Chart 氣泡圖功能
 * 每個氣泡代表一位同學，Y軸為標籤比例，氣泡大小為審查活動參與度
 */

class BubbleChartManager {
    constructor() {
        this.chart = null;
        this.data = null;
        this.init();
    }

    init() {
        this.initChart();
    }

    initChart() {
        const ctx = document.getElementById('bubbleChart').getContext('2d');
        
        this.chart = new Chart(ctx, {
            type: 'bubble',
            data: {
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 80,     // 增加上方 padding
                        right: 40,
                        bottom: 80,  // 增加下方 padding
                        left: 80     // 增加左側 padding 給 Y 軸學生名稱更多空間
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: '全班作業審查狀況多維氣泡圖',
                        font: {
                            size: 18,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return context[0].raw.studentName || `學生 ${context[0].dataIndex + 1}`;
                            },
                            label: function(context) {
                                const data = context.raw;
                                const labelNames = ['相關性', '具體性', '建設性', '總和'];
                                const labelName = labelNames[Math.round(data.x)];
                                const percentage = (data.labelRatio * 100).toFixed(1);
                                
                                // 為總和標籤添加更清晰的說明
                                const percentageText = data.labelType === 3 
                                    ? `${percentage}% (三標籤平均)` 
                                    : `${percentage}%${data.labelRatio > 1 ? ' (多標籤評論)' : ''}`;
                                
                                return [
                                    `品質指標: ${labelName}`,
                                    `標籤比例: ${percentageText}`,
                                    `參與度: ${(data.participation * 100).toFixed(1)}%`,
                                    `有效評論數: ${data.validRounds || data.validComments || 0}`,
                                    `分配任務數: ${data.assignedTasks || 0}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '品質指標'
                        },
                        min: -0.5,
                        max: 3.5,
                        ticks: {
                            stepSize: 1,
                            min: 0,
                            max: 3,
                            callback: function(value, index, values) {
                                const labels = ['相關性', '具體性', '建設性', '總和'];
                                const roundedValue = Math.round(value);
                                if (roundedValue >= 0 && roundedValue < labels.length) {
                                    return labels[roundedValue];
                                }
                                return '';
                            }
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: '學生'
                        },
                        min: -1.5,  // 增加下方空間
                        max: 1.5,   // 增加上方空間（將根據學生數量動態調整）
                        ticks: {
                            stepSize: 1,
                            callback: function(value, index, values) {
                                // 從圖表物件中獲取學生名稱
                                const chart = Chart.getChart(this.ctx);
                                const roundedValue = Math.round(value);
                                if (chart && chart.studentNames && chart.studentNames[roundedValue] && roundedValue >= 0) {
                                    // 截斷過長的學生名稱
                                    const name = chart.studentNames[roundedValue];
                                    return name.length > 10 ? name.substring(0, 10) + '...' : name;
                                }
                                return '';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const element = elements[0];
                        const datasetIndex = element.datasetIndex;
                        const index = element.index;
                        const studentData = this.chart.data.datasets[datasetIndex].data[index];
                        this.showStudentDetails(studentData);
                    }
                }
            }
        });

        // 儲存當前模式到 chart 物件
        this.chart.currentMode = this.currentMode;
    }

    updateChart() {
        if (!this.data) {
            console.log('No data available for bubble chart');
            return;
        }

        const bubbleData = this.prepareBubbleData();
        
        // 為四個品質指標創建不同的數據集
        const datasets = [
            {
                label: '相關性',
                data: bubbleData.filter(d => d.labelType === 0),
                backgroundColor: bubbleData.filter(d => d.labelType === 0).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 0).map(d => d.borderColor),
                borderWidth: 2
            },
            {
                label: '具體性',
                data: bubbleData.filter(d => d.labelType === 1),
                backgroundColor: bubbleData.filter(d => d.labelType === 1).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 1).map(d => d.borderColor),
                borderWidth: 2
            },
            {
                label: '建設性',
                data: bubbleData.filter(d => d.labelType === 2),
                backgroundColor: bubbleData.filter(d => d.labelType === 2).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 2).map(d => d.borderColor),
                borderWidth: 2
            },
            {
                label: '總和',
                data: bubbleData.filter(d => d.labelType === 3),
                backgroundColor: bubbleData.filter(d => d.labelType === 3).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 3).map(d => d.borderColor),
                borderWidth: 2
            }
        ];

        this.chart.data.datasets = datasets;
        this.chart.options.plugins.title.text = '全班作業審查狀況多維氣泡圖';
        
        this.chart.update();
    }

    prepareBubbleData() {
        const students = this.extractStudentData();
        const bubbleData = [];
        const studentNames = [];

        console.log(`準備多維氣泡圖資料：共 ${students.length} 位學生`);

        // 更新 Y 軸範圍，增加上下空間避免壓縮
        this.chart.options.scales.y.min = -1.5;
        this.chart.options.scales.y.max = students.length + 0.5;
        
        students.forEach((student, studentIndex) => {
            studentNames.push(student.name);
            
            const participation = student.validComments / Math.max(student.assignedTasks, 1);
            
            // 為每個品質指標創建氣泡
            const labelTypes = [
                { type: 0, name: 'relevance', displayName: '相關性' },
                { type: 1, name: 'concreteness', displayName: '具體性' },
                { type: 2, name: 'constructive', displayName: '建設性' },
                { type: 3, name: 'all', displayName: '總和' }
            ];
            
            labelTypes.forEach(labelInfo => {
                let labelRatio = 0;
                
                // 計算標籤比例：該品質指標出現次數 / 被分配的所有評論數
                if (labelInfo.type === 3) { // 總和模式 - 三個標籤比例的平均
                    const assignedTasksCount = Math.max(student.assignedTasks, 1);
                    const relevanceRatio = (student.relevanceCount || 0) / assignedTasksCount;
                    const concretenessRatio = (student.concretenessCount || 0) / assignedTasksCount;
                    const constructiveRatio = (student.constructiveCount || 0) / assignedTasksCount;
                    
                    // 總和 = 三個標籤比例的平均
                    labelRatio = (relevanceRatio + concretenessRatio + constructiveRatio) / 3;
                } else {
                    // 單一標籤比例 = 該標籤數量 / 被分配的所有評論數
                    // 這樣計算能正確反映品質指標在所有分配評論中的出現比例
                    const labelCount = student[`${labelInfo.name}Count`] || 0;
                    labelRatio = labelCount / Math.max(student.assignedTasks, 1);
                }
                
                // 氣泡大小：基於參與度，範圍 0.2px-15px
                const bubbleSize = Math.max(Math.min(participation * 15, 15), 0.2);
                
                // 氣泡顏色：基於標籤比例
                const { color, borderColor } = this.getBubbleColorForLabel(labelRatio, labelInfo.type);
                
                bubbleData.push({
                    x: labelInfo.type,     // X軸：品質指標 (0=相關性, 1=具體性, 2=建設性, 3=總和)
                    y: studentIndex,       // Y軸：學生索引
                    r: bubbleSize,         // 氣泡大小：參與度
                    studentName: student.name,
                    studentId: student.id,
                    labelType: labelInfo.type,
                    labelName: labelInfo.displayName,
                    labelRatio: labelRatio,
                    validComments: student.validComments,       // 完成的 Assignment 數（氣泡大小分子）
                    validRounds: student.validRounds,           // 有效的 Round 數（僅供參考）
                    assignedTasks: student.assignedTasks,       // 分配的任務數（氣泡大小和顏色的分母）
                    participation: participation,
                    relevanceCount: student.relevanceCount || 0,
                    concretenessCount: student.concretenessCount || 0,
                    constructiveCount: student.constructiveCount || 0,
                    color: color,
                    borderColor: borderColor
                });
            });
            
            // 除錯：顯示前3個學生的詳細資料
            if (studentIndex < 3) {
                const assignedTasksCount = Math.max(student.assignedTasks, 1);
                const relevanceRatio = (student.relevanceCount || 0) / assignedTasksCount;
                const concretenessRatio = (student.concretenessCount || 0) / assignedTasksCount;
                const constructiveRatio = (student.constructiveCount || 0) / assignedTasksCount;
                const averageRatio = (relevanceRatio + concretenessRatio + constructiveRatio) / 3;
                
                console.log(`學生 ${student.name}:`, {
                    validComments: student.validComments,       // 完成的 Assignment 數
                    validRounds: student.validRounds,           // 有效的 Round 數
                    assignedTasks: student.assignedTasks,       // 被分配的評論數（新的分母）
                    participation: (participation * 100).toFixed(1) + '%',
                    relevanceCount: student.relevanceCount,
                    concretenessCount: student.concretenessCount,
                    constructiveCount: student.constructiveCount,
                    relevanceRatio: (relevanceRatio * 100).toFixed(1) + '%',
                    concretenessRatio: (concretenessRatio * 100).toFixed(1) + '%',
                    constructiveRatio: (constructiveRatio * 100).toFixed(1) + '%',
                    averageRatio: (averageRatio * 100).toFixed(1) + '%',
                    note: '標籤比例 = 標籤數/分配評論數，總和 = 三個標籤比例的平均'
                });
            }
        });
        
        // 儲存學生名稱到 chart 物件，供 Y 軸標籤使用
        this.chart.studentNames = studentNames;
        
        console.log(`多維氣泡圖資料準備完成，共 ${bubbleData.length} 個氣泡`);
        return bubbleData;
    }

    extractStudentData() {
        if (!this.data || !this.data.nodes) {
            return [];
        }

        const students = [];
        this.data.nodes.forEach(node => {
            if (node.group === 'student') {
                students.push({
                    id: node.id,
                    name: node.label,
                    validComments: node.validComments || 0,
                    validRounds: node.validRounds || 0,
                    assignedTasks: node.assignedTasks || 0,
                    relevanceCount: node.relevanceCount || 0,
                    concretenessCount: node.concretenessCount || 0,
                    constructiveCount: node.constructiveCount || 0
                });
            }
        });

        return students;
    }

    getBubbleColorForLabel(labelRatio, labelType) {
        // 4分級顏色計算
        // 計算基礎：標籤出現次數 / 被分配的所有評論數
        // 對於總和模式（labelType=3），比例範圍為0-100%（三個標籤比例的平均）
        // 對於單一標籤模式（labelType=0,1,2），比例範圍通常為0-100%
        let colorLevel;
        
        if (labelType === 3) {
            // 總和模式：0-100% 範圍
            if (labelRatio >= 0.75) colorLevel = 3;      // 最深色 (75%以上)
            else if (labelRatio >= 0.5) colorLevel = 2;  // 深色 (50-75%)
            else if (labelRatio >= 0.25) colorLevel = 1; // 淺色 (25-50%)
            else colorLevel = 0;                          // 最淺色 (25%以下)
        } else {
            // 單一標籤模式：通常0-100% 範圍（標籤數/分配評論數）
            if (labelRatio >= 0.75) colorLevel = 3;      // 最深色 (75%以上)
            else if (labelRatio >= 0.5) colorLevel = 2;  // 深色 (50-75%)
            else if (labelRatio >= 0.25) colorLevel = 1; // 淺色 (25-50%)
            else colorLevel = 0;                          // 最淺色 (25%以下)
        }
        
        // 顏色配置 (與 node color 一致)
        const colorConfigs = [
            { // 相關性
                colors: ["rgba(255, 238, 183, 0.8)", "rgba(255, 215, 83, 0.8)", "rgba(241, 188, 13, 0.8)", "rgba(212, 163, 2, 0.8)"],
                borderColors: ["rgba(255, 238, 183, 1)", "rgba(255, 215, 83, 1)", "rgba(241, 188, 13, 1)", "rgba(212, 163, 2, 1)"]
            },
            { // 具體性
                colors: ["rgba(207, 255, 202, 0.8)", "rgba(149, 237, 101, 0.8)", "rgba(84, 175, 35, 0.8)", "rgba(50, 113, 17, 0.8)"],
                borderColors: ["rgba(207, 255, 202, 1)", "rgba(149, 237, 101, 1)", "rgba(84, 175, 35, 1)", "rgba(50, 113, 17, 1)"]
            },
            { // 建設性
                colors: ["rgba(241, 220, 255, 0.8)", "rgba(199, 142, 237, 0.8)", "rgba(148, 68, 202, 0.8)", "rgba(89, 10, 142, 0.8)"],
                borderColors: ["rgba(241, 220, 255, 1)", "rgba(199, 142, 237, 1)", "rgba(148, 68, 202, 1)", "rgba(89, 10, 142, 1)"]
            },
            { // 總和
                colors: ["rgba(240, 240, 240, 0.8)", "rgba(224, 224, 224, 0.8)", "rgba(117, 117, 117, 0.8)", "rgba(66, 66, 66, 0.8)"],
                borderColors: ["rgba(240, 240, 240, 1)", "rgba(224, 224, 224, 1)", "rgba(117, 117, 117, 1)", "rgba(66, 66, 66, 1)"]
            }
        ];
        
        const config = colorConfigs[labelType];
        return {
            color: config.colors[colorLevel],
            borderColor: config.borderColors[colorLevel]
        };
    }

    showStudentDetails(studentData) {
        const modal = document.createElement('div');
        modal.className = 'student-detail-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${studentData.studentName || `學生 ${studentData.studentId}`}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="detail-row">
                        <span class="detail-label">有效評論數：</span>
                        <span class="detail-value">${studentData.validRounds || studentData.validComments}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">完成任務數：</span>
                        <span class="detail-value">${studentData.validComments}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">分配任務數：</span>
                        <span class="detail-value">${studentData.assignedTasks}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">參與度：</span>
                        <span class="detail-value">${(studentData.participation * 100).toFixed(1)}%</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">相關性標籤：</span>
                        <span class="detail-value">${studentData.relevanceCount}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">具體性標籤：</span>
                        <span class="detail-value">${studentData.concretenessCount}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">建設性標籤：</span>
                        <span class="detail-value">${studentData.constructiveCount}</span>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 關閉模態框事件
        const closeBtn = modal.querySelector('.modal-close');
        const closeModal = () => document.body.removeChild(modal);
        
        closeBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        // ESC 鍵關閉
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    updateData(data) {
        this.data = data;
        this.updateChart();
    }
}

// 匯出供其他模組使用
window.BubbleChartManager = BubbleChartManager;
