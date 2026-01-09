// 全作業標籤頻率統計圖表 - Node.js版本
const fs = require('fs');
const path = require('path');
const { createCanvas } = require('canvas');
const Chart = require('chart.js/auto');

// 載入3標籤資料
function load3LabelData() {
    try {
        const dataPath = path.join(__dirname, '../function/3labeled_processed_totalData.json');
        const rawData = fs.readFileSync(dataPath, 'utf8');
        return JSON.parse(rawData);
    } catch (error) {
        console.error('Error loading 3label data:', error);
        return null;
    }
}

// 計算每個作業的3標籤出現頻率
function calculateHwLabelFrequency(data) {
    const hwStats = {};
    
    // 初始化統計結構
    Object.keys(data).forEach(hwName => {
        hwStats[hwName] = {
            total: 0,
            relevance: 0,
            concreteness: 0,
            constructive: 0
        };
    });
    
    // 統計每個作業的標籤頻率
    Object.entries(data).forEach(([hwName, hwData]) => {
        hwData.forEach(student => {
            if (student.Round && Array.isArray(student.Round)) {
                student.Round.forEach(round => {
                    // 只統計有完整資料的回合
                    if (round.Relevance !== undefined && round.Concreteness !== undefined && round.Constructive !== undefined) {
                        hwStats[hwName].total++;
                        if (round.Relevance === 1) hwStats[hwName].relevance++;
                        if (round.Concreteness === 1) hwStats[hwName].concreteness++;
                        if (round.Constructive === 1) hwStats[hwName].constructive++;
                    }
                });
            }
        });
    });
    
    // 計算百分比
    const percentageStats = {};
    Object.entries(hwStats).forEach(([hwName, stats]) => {
        if (stats.total > 0) {
            percentageStats[hwName] = {
                relevance: (stats.relevance / stats.total) * 100,
                concreteness: (stats.concreteness / stats.total) * 100,
                constructive: (stats.constructive / stats.total) * 100,
                total: stats.total
            };
        } else {
            percentageStats[hwName] = {
                relevance: 0,
                concreteness: 0,
                constructive: 0,
                total: 0
            };
        }
    });
    
    return percentageStats;
}

// 創建圖表
function createHwLabelChart(stats) {
    // 創建 Canvas
    const canvas = createCanvas(800, 600);
    const ctx = canvas.getContext('2d');
    
    // 準備資料
    const hwNames = Object.keys(stats).sort(); // 排序作業名稱
    const relevanceData = hwNames.map(hw => stats[hw].relevance);
    const concretenessData = hwNames.map(hw => stats[hw].concreteness);
    const constructiveData = hwNames.map(hw => stats[hw].constructive);
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: hwNames,
            datasets: [
                {
                    label: 'Relevance',
                    data: relevanceData,
                    backgroundColor: 'rgba(255, 206, 84, 0.8)',
                    borderColor: 'rgba(255, 206, 84, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Concreteness',
                    data: concretenessData,
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Constructive',
                    data: constructiveData,
                    backgroundColor: 'rgba(153, 102, 255, 0.8)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: false,
            animation: false,
            plugins: {
                title: {
                    display: true,
                    text: '全作業3標籤出現頻率統計',
                    font: {
                        size: 18,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '作業名稱',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '出現頻率 (%)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            elements: {
                bar: {
                    borderWidth: 2
                }
            }
        }
    });
    
    return { chart, canvas };
}

// 保存圖表為PNG
function saveChartAsPNG(canvas, filename = 'hwLabelChart.png') {
    const outputPath = path.join(__dirname, filename);
    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buffer);
    console.log(`圖表已保存至: ${outputPath}`);
}

// 主要執行函數
async function initHwLabelChart() {
    console.log('開始載入3標籤資料...');
    
    const data = load3LabelData();
    if (!data) {
        console.error('無法載入3標籤資料');
        return;
    }
    
    console.log('計算標籤頻率統計...');
    const stats = calculateHwLabelFrequency(data);
    console.log('標籤頻率統計結果:', stats);
    
    // 創建圖表
    const { chart, canvas } = createHwLabelChart(stats);
    
    // 保存為PNG
    saveChartAsPNG(canvas, 'hwLabelChart.png');
    
    // 顯示統計摘要
    displayStatsSummary(stats);
}

// 顯示統計摘要
function displayStatsSummary(stats) {
    console.log('\n=== 統計摘要 ===');
    console.log('作業\t\tRelevance (%)\tConcreteness (%)\tConstructive (%)\t總評論數');
    console.log('---'.repeat(25));
    
    Object.entries(stats).sort().forEach(([hwName, data]) => {
        console.log(`${hwName}\t\t${data.relevance.toFixed(1)}%\t\t${data.concreteness.toFixed(1)}%\t\t${data.constructive.toFixed(1)}%\t\t${data.total}`);
    });
}

// 導出函數
module.exports = { initHwLabelChart, calculateHwLabelFrequency, createHwLabelChart, saveChartAsPNG };

// 如果直接執行此檔案
if (require.main === module) {
    initHwLabelChart();
}