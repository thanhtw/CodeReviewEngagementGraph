import { processReviewerData } from './graph_func.js';

export function updateNetworkInstance(container, data, options, rawData) {
    if (window.networkInstance) {
        // 停止物理引擎避免殘留動畫
        window.networkInstance.setOptions({ physics: { enabled: false } });
        // 徹底清除舊資料
        window.networkInstance.setData({ nodes: [], edges: [] });
        // 設定新資料和選項
        window.networkInstance.setData(data);
        window.networkInstance.setOptions({ ...options, physics: { enabled: true } });
        // 強制重繪
        window.networkInstance.redraw();
    } else {
        window.networkInstance = new vis.Network(container, data, options);
        window.networkInstance.on('click', function(properties) {
            if (properties.nodes.length > 0) {
                const nodeId = properties.nodes[0];
                const nodeData = new vis.DataSet(data.nodes).get(nodeId);
                const selectedHWs = Array.from(document.getElementById('hw-select').selectedOptions)
                                        .map(opt => opt.value);
                const reviewerRecords = selectedHWs.flatMap(hwName => 
                    rawData[hwName]?.filter(a => a.Reviewer_Name === nodeId) || []
                );
                console.log("審查任務:", reviewerRecords);
            }
        });
    }
}

export function generateGraph(rawData, mode, hwNames) {
    const container = document.getElementById('review-graph');
    if (!container) return;

    // 資料處理
    const { nodes, links } = processReviewerData(rawData, mode, hwNames);

    // 節點大小計算 - 改為 Assignment 層級的參與度（與氣泡圖一致）
    const allCompletionRates = nodes.map(n => {
        // 計算有多少個 Assignment 有有效評論
        const assignmentCount = n.feedbacks.length; // 總分配的 Assignment 數
        const completedAssignments = n.feedbacks.filter(fb => fb !== "").length; // 完成的 Assignment 數
        return assignmentCount > 0 ? completedAssignments / assignmentCount : 0;
    });
    const minRate = Math.min(...allCompletionRates);
    const maxRate = Math.max(...allCompletionRates);
    const sizeScale = (rate) => 15 + (rate * 35); // 15-50 的範圍

    // 節點顏色規則 (4個分級)
    const colorConfig = {
        relevance: { 
            colors: ["#FFEEB7", "#FFD753", "#F1BC0D", "#D4A302"], 
            title: '相關性分數' 
        },
        concreteness: { 
            colors: ["#CFFFCA", "#95ED65", "#54AF23", "#327111"], 
            title: '具體性分數' 
        },
        constructive: { 
            colors: ["#F1DCFF", "#C78EED", "#9444CA", "#590A8E"], 
            title: '建設性分數' 
        },
        all: {
            colors: ["#F0F0F0", "#E0E0E0", "#757575", "#424242"],
            title: '綜合表現分數'
        }
    };

    // 節點樣式
    const visNodes = nodes.map(n => {
        // Assignment 層級的參與度計算（與氣泡圖一致）
        const assignmentCount = n.feedbacks.length; // 總分配的 Assignment 數
        const completedAssignments = n.feedbacks.filter(fb => fb !== "").length; // 完成的 Assignment 數
        const completionRate = assignmentCount > 0 ? completedAssignments / assignmentCount : 0;
        
        // 保持原有的分數計算邏輯（用於顏色）
        const totalFeedbacks = n.feedbacks.filter(fb => fb !== "").length;
        let score;
        
        // 計算分數邏輯
        if (mode === 'all') {
            // All mode: 計算三個標籤score的平均
            if (totalFeedbacks > 0) {
                const relevanceScore = n.labelCounts.relevance / totalFeedbacks;
                const concretenessScore = n.labelCounts.concreteness / totalFeedbacks;
                const constructiveScore = n.labelCounts.constructive / totalFeedbacks;
                score = (relevanceScore + concretenessScore + constructiveScore) / 3;
                
                // 除錯資訊：只顯示前3個節點的詳細計算
                if (n.id === 'D1018525' || Math.random() < 0.05) {
                    console.log(`[All Mode] 審查者 ${n.id}:`);
                    console.log(`  總分配Assignment: ${assignmentCount}`);
                    console.log(`  完成Assignment數: ${completedAssignments}`);
                    console.log(`  審查參與度: ${(completionRate * 100).toFixed(1)}%`);
                    console.log(`  有效評論Round數: ${totalFeedbacks}`);
                    console.log(`  相關性標籤: ${n.labelCounts.relevance} (score: ${relevanceScore.toFixed(3)})`);
                    console.log(`  具體性標籤: ${n.labelCounts.concreteness} (score: ${concretenessScore.toFixed(3)})`);
                    console.log(`  建設性標籤: ${n.labelCounts.constructive} (score: ${constructiveScore.toFixed(3)})`);
                    console.log(`  All mode score: ${score.toFixed(3)}`);
                }
            } else {
                score = 0;
            }
        } else {
            // 單一標籤模式
            score = totalFeedbacks > 0 ? n.labelCounts[mode] / totalFeedbacks : 0;
        }
        
        // 4分級顏色計算
        let color;
        if (score >= 0.75) color = colorConfig[mode].colors[3];      // 最深色 (75%以上)
        else if (score >= 0.5) color = colorConfig[mode].colors[2]; // 深色 (50-75%)
        else if (score >= 0.25) color = colorConfig[mode].colors[1]; // 淺色 (25-50%)
        else color = colorConfig[mode].colors[0];                   // 最淺色 (25%以下)

        return {
            id: n.id,
            label: n.id,
            value: sizeScale(completionRate), // 使用 Assignment 層級的參與度計算大小
            color: { background: color, border: color },
            borderWidth: 0,
            shape: "dot",
            title: `審查者: ${n.id}\n${colorConfig[mode].title}: ${Math.round(score * 100)}%\n審查參與度: ${Math.round(completionRate * 100)}%`
        };
    });

    // 邊樣式
    const visEdges = links.map(e => ({
        from: e.from,
        to: e.to,
        color: { color: e.completedAll ? "#73BEFF" : "#ff6b6b", highlight: e.completedAll ? "#73BEFF" : "#ff6b6b" },
        dashes: !e.completedAll,
        arrows: "to",
        width: 1.5
    }));

    // 建立 DataSet 和 options
    const data = { nodes: new vis.DataSet(visNodes), edges: new vis.DataSet(visEdges) };
    const options = {
        nodes: {
            scaling: {
                min: 20,
                max: 60,
                label: {
                    enabled: true,
                    min: 12,
                    max: 20
                }
            }
        },
        edges: {
            arrowStrikethrough: false,
            selectionWidth: 3
        },
        physics: {
            stabilization: {
                iterations: 100,
                fit: true
            },
            barnesHut: {
                gravitationalConstant: -2000,
                springLength: 150,
                damping: 0.5
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200
        }
    };

    // 更新實例
    updateNetworkInstance(container, data, options, rawData);
}

export function generateRelevanceGraph(rawData, hwNames = ['HW1']) {
    generateGraph(rawData, 'relevance', hwNames);
}

export function generateConcretenessGraph(rawData, hwNames = ['HW1']) {
    generateGraph(rawData, 'concreteness', hwNames);
}

export function generateConstructiveGraph(rawData, hwNames = ['HW1']) {
    generateGraph(rawData, 'constructive', hwNames);
}

export function generateAllGraph(rawData, hwNames = ['HW1']) {
    generateGraph(rawData, 'all', hwNames);
}
