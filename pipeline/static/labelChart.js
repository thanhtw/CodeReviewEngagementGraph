let cooccurrenceChart = null;
let probabilityChart = null;
let combinedProbabilityChart = null;

export function runAnalysis() {
    // Parse input data
    const inputData = JSON.parse(document.getElementById('inputData').value);
    const allLabels = [...new Set(inputData.flatMap(d => d.labels))].sort();
    
    // Calculate co-occurrence matrix
    const coMatrix = calculateCooccurrenceMatrix(inputData, allLabels);
    
    // Calculate conditional probability
    const condProb = calculateConditionalProbability(coMatrix, allLabels);
    
    // Destroy old charts
    if(cooccurrenceChart) cooccurrenceChart.destroy();
    if(probabilityChart) probabilityChart.destroy();
    
    // Draw new charts
    renderCooccurrenceChart(coMatrix, allLabels);
    renderConditionalProbChart(condProb);
}

export function calculateCooccurrenceMatrix(data, labels) {
    // Initialize matrix
    const matrix = Array(labels.length).fill()
        .map(() => Array(labels.length).fill(0));
    
    // Fill co-occurrence counts
    data.forEach(entry => {
        entry.labels.forEach((label1, i) => {
            entry.labels.slice(i+1).forEach(label2 => {
                const x = labels.indexOf(label1);
                const y = labels.indexOf(label2);
                matrix[x][y]++;
                matrix[y][x]++;
            });
        });
    });
    
    return matrix;
}  // Calculate contribution matrix

export function calculateConditionalProbability(matrix, labels) {
    // Calculate marginal probability
    const total = matrix.flat().reduce((a,b) => a + b, 0);
    const marginal = matrix.map(row => row.reduce((a,b) => a + b, 0)/total);
    
    // Calculate conditional probability
    return matrix.map((row, i) => 
        row.map((count, j) => 
            count > 0 ? count / (marginal[i] * total) : 0
        )
    );
}  // Calculate conditional probability

// Chart destroy function
export function destroyCharts() {
    if (cooccurrenceChart) {
        cooccurrenceChart.destroy();
        cooccurrenceChart = null;
    }
    if (probabilityChart) {
        probabilityChart.destroy();
        probabilityChart = null;
    }
    if (combinedProbabilityChart) {
        combinedProbabilityChart.destroy();
        combinedProbabilityChart = null;
    }
    if (window.correlationChart) {
        window.correlationChart.destroy();
        window.correlationChart = null;
    }
}


export function renderCooccurrenceChart(matrix, labels) {
    const ctx = document.getElementById('cooccurrenceChart');
    if (!ctx) return;
    
    // Convert to matrix chart format
    const matrixData = labels.flatMap((xLabel, x) => 
        labels.map((yLabel, y) => ({
            x: xLabel,
            y: yLabel, 
            value: matrix[x][y]
        }))
    ).filter(item => item.value > 0); // Only show co-occurring data
    const maxValue = Math.max(...matrixData.map(d => d.value));

    cooccurrenceChart = new Chart(ctx.getContext('2d'), {
        type: 'matrix',
        data: {
            datasets: [{
                label: 'Co-occurrence Frequency',
                data: matrixData,
                backgroundColor: (ctx) => {
                    const value = ctx.dataset.data[ctx.dataIndex].value;
                    return `rgba(255, 99, 132, ${Math.max(0.1, Math.min(value / maxValue, 1))})`;
                },
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: { 
                    type: 'category',
                    title: { display: true, text: 'Label' }
                },
                y: { 
                    type: 'category', 
                    title: { display: true, text: 'Label' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: (context) => {
                            const data = context[0].dataset.data[context[0].dataIndex];
                            return `${data.x} × ${data.y}`;
                        },
                        label: (context) => {
                            return `Co-occurrence count: ${context.dataset.data[context.dataIndex].value}`;
                        }
                    }
                }
            }
        }
    });
}

export function renderConditionalProbChart(probMatrix) {
    const ctx = document.getElementById('probabilityChart');
    if (!ctx) {
        console.error('Cannot find probabilityChart element');
        return;
    }

    // Destroy old chart
    if (probabilityChart) probabilityChart.destroy();

    // Define specific label names
    const labelNames = ['relevance', 'concreteness', 'constructive'];

    probabilityChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labelNames,
            datasets: [{
                label: 'Occurrence Frequency',
                data: probMatrix.map(row => Math.max(...row)),
                backgroundColor: 'rgba(54, 162, 235, 0.5)'
            }]
        },
        options: {
            scales: {
                y: {
                    title: { display: true, text: 'Frequency Value' },
                    min: 0,
                    max: 1
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${(context.parsed.y * 100).toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

export function renderCombinedProbChart(selectedData, labels) {
    const ctx = document.getElementById('combinedProbabilityChart');
    if (!ctx) {
        console.error('Cannot find combinedProbabilityChart element');
        return;
    }

    if (combinedProbabilityChart) {  // Destroy old chart
            combinedProbabilityChart.destroy();
            combinedProbabilityChart = null;
        }
    
    if (!selectedData || !Array.isArray(selectedData)) {  // Ensure data exists
        console.error('selectedData invalid:', selectedData);
        return;
    }

    // Use triple label co-occurrence calculation
    const stats = calculateTripleCooccurrence(selectedData, labels);
    const combinedProbs = calculateCombinedConditionalProb(stats, labels);
    const maxValue = Math.max(...Object.values(combinedProbs));
    const dynamicMax = Math.max(0.3, maxValue * 1.5); // At least 0.3, or 1.5x max value

    console.log('Combined conditional probability result:', combinedProbs);
    console.log('Dynamic max value:', dynamicMax);

    combinedProbabilityChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: Object.keys(combinedProbs),
            datasets: [{
                label: 'Combined Conditional Probability',
                data: Object.values(combinedProbs),
                backgroundColor: 'rgba(255, 99, 132, 0.5)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { 
                    min: 0, 
                    max: dynamicMax,
                    title: { display: true, text: 'Probability Value' }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: ${(context.parsed.y * 100).toFixed(2)}%`;
                        }
                    }
                }
            }
        }
    });
}

// Simplified combined conditional probability calculation
export function calculateCombinedConditionalProb(stats, labels) {
    const safeDivide = (numerator, denominator) => {
        return (denominator && denominator > 0) ? numerator / denominator : 0;
    };

    // Generate correct keys
    const relConstKey = ['constructive', 'relevance'].sort().join('→');
    const concConstKey = ['concreteness', 'constructive'].sort().join('→');
    const relConcKey = ['concreteness', 'relevance'].sort().join('→');
    const tripleKey = [...labels].sort().join('→');

    const combinedProbs = {
        'rel→const': safeDivide(
            stats.double[relConstKey] || 0, 
            stats.single.relevance || 1
        ),
        'conc→const': safeDivide(
            stats.double[concConstKey] || 0, 
            stats.single.concreteness || 1
        ),
        'rel+conc→const': safeDivide(
            stats.triple[tripleKey] || 0, 
            stats.double[relConcKey] || 1
        )
    };

    return combinedProbs;
}



export function calculateTripleCooccurrence(data, labels) {
    const stats = {
        single: {},
        double: {},
        triple: {}
    };
    
    // Initialize statistics object
    labels.forEach(label => {
        stats.single[label] = 0;
    });
    
    // Calculate various combinations
    data.forEach(entry => {
        const entryLabels = entry.labels || [];
        
        // Single label statistics
        entryLabels.forEach(label => {
            if (stats.single[label] !== undefined) {
                stats.single[label]++;
            }
        });
        
        // Double label co-occurrence statistics
        for (let i = 0; i < entryLabels.length; i++) {
            for (let j = i + 1; j < entryLabels.length; j++) {
                const pair = [entryLabels[i], entryLabels[j]].sort().join('→');
                stats.double[pair] = (stats.double[pair] || 0) + 1;
            }
        }
        
        // Triple label co-occurrence statistics - fixed version
        if (entryLabels.length === 3) {
            const hasAll = labels.every(label => entryLabels.includes(label));
            if (hasAll) {
                // Fix: Use copy to avoid modifying original array
                const tripleKey = [...labels].sort().join('→');
                stats.triple[tripleKey] = (stats.triple[tripleKey] || 0) + 1;
            }
        }
    });
    
    console.log('Debug - Statistics result:', stats); // Important debug info
    return stats;
}

export function calculateAdvancedConditionalProb(stats, labels) {
    const safeDivide = (numerator, denominator) => {
        return (denominator && denominator > 0) ? numerator / denominator : 0;
    };
    
    // Generate correct keys
    const sortedLabels = [...labels].sort(); // Ensure consistency with calculation order
    const relConstKey = ['constructive', 'relevance'].sort().join('→');
    const concConstKey = ['concreteness', 'constructive'].sort().join('→');
    const relConcKey = ['concreteness', 'relevance'].sort().join('→');
    const tripleKey = sortedLabels.join('→');
    
    console.log('Debug - Keys:', { relConstKey, concConstKey, relConcKey, tripleKey });
    console.log('Debug - Double stats:', stats.double);
    console.log('Debug - Triple stats:', stats.triple);
    
    // Single label conditional probability
    const singleProbs = {
        'relevance → others': safeDivide(
            (stats.double[relConcKey] || 0) + (stats.double[relConstKey] || 0), 
            stats.single.relevance
        ),
        'concreteness → others': safeDivide(
            (stats.double[relConcKey] || 0) + (stats.double[concConstKey] || 0), 
            stats.single.concreteness
        ),
        'constructive → others': safeDivide(
            (stats.double[relConstKey] || 0) + (stats.double[concConstKey] || 0), 
            stats.single.constructive
        )
    };
    
    // Combined conditional probability
    const combinedProbs = {
        'relevance → constructive': safeDivide(
            stats.double[relConstKey] || 0, 
            stats.single.relevance
        ),
        'concreteness → constructive': safeDivide(
            stats.double[concConstKey] || 0, 
            stats.single.concreteness
        ),
        'relevance+concreteness → constructive': safeDivide(
            stats.triple[tripleKey] || 0, 
            stats.double[relConcKey] || 1
        )
    };
    
    console.log('Debug - Calculation result:', { singleProbs, combinedProbs });
    return { singleProbs, combinedProbs };
}

// Multi-label combined conditional probability
export function calculateDetailedConditionalAnalysis(selectedData, labels) {
    const analysis = {
        singleConditions: {},
        doubleConditions: {},
        insights: []
    };
    
    // Calculate statistics under various conditions
    const stats = {
        total: selectedData.length,
        single: {},
        pairs: {},
        triples: {}
    };
    
    // Count single label occurrences
    labels.forEach(label => {
        stats.single[label] = selectedData.filter(d => 
            d.labels.includes(label)
        ).length;
    });
    
    // Count label pair co-occurrences
    for (let i = 0; i < labels.length; i++) {
        for (let j = i + 1; j < labels.length; j++) {
            const labelA = labels[i];
            const labelB = labels[j];
            const pairKey = `${labelA}+${labelB}`;
            
            stats.pairs[pairKey] = selectedData.filter(d => 
                d.labels.includes(labelA) && d.labels.includes(labelB)
            ).length;
        }
    }
    
    // Count triple label co-occurrences
    if (labels.length === 3) {
        const tripleKey = labels.join('+');
        stats.triples[tripleKey] = selectedData.filter(d => 
            labels.every(label => d.labels.includes(label))
        ).length;
    }
    
    // Calculate conditional probability
    // 1. Single condition: P(constructive | relevance)
    analysis.singleConditions = {
        'constructive_given_relevance': stats.pairs['relevance+constructive'] / stats.single.relevance,
        'constructive_given_concreteness': stats.pairs['concreteness+constructive'] / stats.single.concreteness,
        'relevance_given_constructive': stats.pairs['relevance+constructive'] / stats.single.constructive,
        'concreteness_given_constructive': stats.pairs['concreteness+constructive'] / stats.single.constructive
    };
    
    // 2. Double condition: P(constructive | relevance AND concreteness)
    const bothRelConc = stats.pairs['relevance+concreteness'] || 1;
    const allThree = stats.triples[labels.join('+')] || 0;
    
    analysis.doubleConditions = {
        'constructive_given_both_rel_conc': allThree / bothRelConc
    };
    
    // Generate analysis insights
    analysis.insights = generateInsights(analysis, stats);
    
    return { analysis, stats };
}

// Generate analysis insights
function generateInsights(analysis, stats) {
    const insights = [];
    const t = (key, fallback) => window.i18n?.t(key) || fallback;
    
    const singleProb = analysis.singleConditions.constructive_given_relevance || 0;
    const doubleProb = analysis.doubleConditions.constructive_given_both_rel_conc || 0;
    
    if (doubleProb > singleProb) {
        const improvement = ((doubleProb - singleProb) / singleProb * 100).toFixed(1);
        const relevance = t('graph.relevance', '相關性');
        const concreteness = t('graph.concreteness', '具體性');
        const constructiveness = t('graph.constructiveness', '建設性');
        insights.push({
            type: 'positive_correlation',
            message: `${t('chart.both_labels_insight', '當評論同時具有相關性和具體性時')}，${constructiveness}: ${(doubleProb * 100).toFixed(1)}% (vs ${(singleProb * 100).toFixed(1)}%) +${improvement}%`,
            strength: doubleProb > 0.7 ? 'strong' : doubleProb > 0.5 ? 'moderate' : 'weak'
        });
    }
    
    // 比較不同單條件的效果
    const relProb = analysis.singleConditions.constructive_given_relevance || 0;
    const concProb = analysis.singleConditions.constructive_given_concreteness || 0;
    
    if (Math.abs(relProb - concProb) > 0.1) {
        const stronger = relProb > concProb ? t('graph.relevance', '相關性') : t('graph.concreteness', '具體性');
        const stronger_prob = Math.max(relProb, concProb);
        const weaker_prob = Math.min(relProb, concProb);
        
        insights.push({
            type: 'differential_impact',
            message: `${stronger} ${t('chart.stronger_prediction', '對建設性的預測能力更強')}（${(stronger_prob * 100).toFixed(1)}% vs ${(weaker_prob * 100).toFixed(1)}%）`,
            strength: 'informative'
        });
    }
    
    return insights;
}
// 在 renderCombinedProbChart 後添加文字分析
export function renderAnalysisInsights(selectedData, labels) {
    const { analysis, stats } = calculateDetailedConditionalAnalysis(selectedData, labels);
    
    // 找到或創建分析展示區域
    let insightContainer = document.getElementById('analysis-insights');
    if (!insightContainer) {
        insightContainer = document.createElement('div');
        insightContainer.id = 'analysis-insights';
        insightContainer.className = 'analysis-insights';
        
        // 插入到組合條件機率圖表後面
        const combinedChart = document.getElementById('combinedProbabilityChart').parentElement;
        combinedChart.parentElement.insertBefore(insightContainer, combinedChart.nextSibling);
    }
    
    // 生成 HTML 內容
    const t = (key, fallback) => window.i18n?.t(key) || fallback;
    let html = `<h3>${t('chart.insight_title', '條件機率分析洞察')}</h3><div class="insights-content">`;
    
    // 顯示詳細數據
    html += '<div class="stats-summary">';
    html += `<p><strong>${t('chart.data_overview', '數據概覽')}：</strong>${t('chart.total_reviews', '總評論數')} ${stats.total}，`;
    html += `${t('graph.relevance', '相關性')} ${stats.single.relevance}，${t('graph.concreteness', '具體性')} ${stats.single.concreteness}，${t('graph.constructiveness', '建設性')} ${stats.single.constructive}</p>`;
    html += '</div>';
    
    // 顯示洞察
    analysis.insights.forEach(insight => {
        const strengthClass = insight.strength === 'strong' ? 'insight-strong' : 
                            insight.strength === 'moderate' ? 'insight-moderate' : 'insight-weak';
        html += `<div class="insight-item ${strengthClass}">`;
        html += `<i class="insight-icon">📊</i>`;
        html += `<span>${insight.message}</span>`;
        html += '</div>';
    });
    
    // 顯示具體機率數值
    html += '<div class="detailed-probabilities">';
    html += `<h4>${t('chart.detailed_probabilities', '詳細條件機率')}：</h4>`;
    html += '<ul>';
    html += `<li>${t('chart.prob_constructive_given_relevance', 'P(建設性|相關性)')} = ${(analysis.singleConditions.constructive_given_relevance * 100).toFixed(1)}%</li>`;
    html += `<li>${t('chart.prob_constructive_given_concreteness', 'P(建設性|具體性)')} = ${(analysis.singleConditions.constructive_given_concreteness * 100).toFixed(1)}%</li>`;
    html += `<li>P(${t('graph.constructiveness', '建設性')}|${t('graph.relevance', '相關性')}∧${t('graph.concreteness', '具體性')}) = ${(analysis.doubleConditions.constructive_given_both_rel_conc * 100).toFixed(1)}%</li>`;
    html += '</ul>';
    html += '</div>';
    
    html += '</div>';
    insightContainer.innerHTML = html;
}

// 計算相關矩陣並繪製熱力圖
export function correlationMatrix(selectedData, labels = ['relevance', 'concreteness', 'constructive']) {
    const canvasElement = document.getElementById('correlationMatrix');
    if (!canvasElement) {
        console.error('找不到 correlationMatrix 元素');
        return;
    }

    // 銷毀舊圖表
    if (window.correlationChart) {
        window.correlationChart.destroy();
        window.correlationChart = null;
    }

    if (!selectedData || !Array.isArray(selectedData)) {
        console.error('selectedData 無效:', selectedData);
        return;
    }

    // 計算相關矩陣
    const correlationData = calculateCorrelationMatrix(selectedData, labels);
    
    // 創建自訂熱力圖
    createCorrelationHeatmap(canvasElement, correlationData, labels);

    return correlationData;
}

// 根據相關係數值獲取顏色
function getCorrelationColor(value) {
    // 使用藍色-白色-紅色漸變
    if (value >= 0) {
        // 正相關：白色到藍色
        const intensity = Math.abs(value);
        const blue = Math.round(255 * intensity);
        const other = Math.round(255 * (1 - intensity));
        return `rgb(${other}, ${other}, 255)`;
    } else {
        // 負相關：白色到紅色
        const intensity = Math.abs(value);
        const red = Math.round(255 * intensity);
        const other = Math.round(255 * (1 - intensity));
        return `rgb(255, ${other}, ${other})`;
    }
}

// 創建相關矩陣熱力圖 (高清晰度版本)
function createCorrelationHeatmap(canvas, matrix, labels) {
    const ctx = canvas.getContext('2d');
    
    // 獲取設備像素比例，確保高 DPI 顯示清晰
    const devicePixelRatio = window.devicePixelRatio || 1;
    
    // 設置顯示尺寸
    const displayWidth = 800;
    const displayHeight = 800;
    
    // 設置實際 canvas 尺寸（考慮設備像素比）
    canvas.width = displayWidth * devicePixelRatio;
    canvas.height = displayHeight * devicePixelRatio;
    
    // 設置 CSS 尺寸
    canvas.style.width = displayWidth + 'px';
    canvas.style.height = displayHeight + 'px';
    
    // 縮放繪圖上下文以匹配設備像素比
    ctx.scale(devicePixelRatio, devicePixelRatio);
    
    // 啟用抗鋸齒
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    
    // 清除畫布
    ctx.clearRect(0, 0, displayWidth, displayHeight);
    
    const cellSize = 150; // 固定較大的格子尺寸
    const startX = 140;   // 增加左邊距給Y軸標籤更多空間
    const startY = 120;
    
    // 設置高品質字體
    ctx.font = `${16 * devicePixelRatio}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // 繪製矩陣格子
    for (let i = 0; i < labels.length; i++) {
        for (let j = 0; j < labels.length; j++) {
            const value = matrix[i][j];
            const x = startX + j * cellSize;
            const y = startY + i * cellSize;
            
            // 根據相關係數設置顏色
            const color = getCorrelationColor(value);
            ctx.fillStyle = color;
            ctx.fillRect(x, y, cellSize, cellSize);
            
            // 繪製邊框
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 2 * devicePixelRatio;
            ctx.strokeRect(x, y, cellSize, cellSize);
            
            // 繪製數值
            ctx.fillStyle = value > 0.5 ? '#fff' : '#000';
            ctx.font = `bold ${14 * devicePixelRatio}px Arial`;
            ctx.fillText(value.toFixed(2), x + cellSize/2, y + cellSize/2);
        }
    }
    
    // 繪製行標籤 (Y軸)
    ctx.fillStyle = '#000';
    ctx.font = `${14 * devicePixelRatio}px Arial`;
    ctx.textAlign = 'right';
    for (let i = 0; i < labels.length; i++) {
        const y = startY + i * cellSize + cellSize/2;
        ctx.fillText(labels[i], startX - 7, y); // 增加距離避免壓縮
    }
    
    // 繪製列標籤 (X軸)
    ctx.textAlign = 'center';
    ctx.save();
    for (let j = 0; j < labels.length; j++) {
        const x = startX + j * cellSize + cellSize/2;
        ctx.translate(x, startY - 60); // 往上移動避免重疊
        ctx.rotate(-Math.PI/4);
        ctx.fillText(labels[j], 0, 0);
        ctx.restore();
        ctx.save();
    }
    ctx.restore();
    
    // 繪製標題
    ctx.textAlign = 'center';
    ctx.font = `bold ${18 * devicePixelRatio}px Arial`;
    //ctx.fillText('標籤相關係數矩陣 (Canvas版本)', displayWidth/2, 40);
    
    // 繪製色條圖例
    drawColorScale(ctx, displayWidth - 120, startY, 30, cellSize * labels.length, devicePixelRatio);
}

// 繪製色條圖例 (高 DPI 版本)
function drawColorScale(ctx, x, y, width, height, devicePixelRatio = 1) {
    const steps = 100;
    const stepHeight = height / steps;
    
    // 繪製漸變色條
    for (let i = 0; i < steps; i++) {
        const value = 1 - (i / steps) * 2; // 從 1 到 -1
        const color = getCorrelationColor(value);
        ctx.fillStyle = color;
        ctx.fillRect(x, y + i * stepHeight, width, stepHeight);
    }
    
    // 繪製邊框
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 1 * devicePixelRatio;
    ctx.strokeRect(x, y, width, height);
    
    // 繪製刻度
    ctx.fillStyle = '#000';
    ctx.font = `${10 * devicePixelRatio}px Arial`;
    ctx.textAlign = 'left';
    
    const labels = ['1.0', '0.5', '0.0', '-0.5', '-1.0'];
    for (let i = 0; i < labels.length; i++) {
        const labelY = y + (i * height / 4);
        ctx.fillText(labels[i], x + width + 5, labelY);
    }
}

// 計算皮爾森相關係數矩陣
function calculateCorrelationMatrix(data, labels) {
    const matrix = Array(labels.length).fill().map(() => Array(labels.length).fill(0));
    
    // 為每個標籤創建二進制向量 (1表示存在，0表示不存在)
    const vectors = labels.map(label => 
        data.map(entry => entry.labels.includes(label) ? 1 : 0)
    );
    
    // 計算每對標籤之間的皮爾森相關係數
    for (let i = 0; i < labels.length; i++) {
        for (let j = 0; j < labels.length; j++) {
            if (i === j) {
                matrix[i][j] = 1; // 自相關為1
            } else {
                matrix[i][j] = calculatePearsonCorrelation(vectors[i], vectors[j]);
            }
        }
    }
    
    return matrix;
}

// 計算皮爾森相關係數
function calculatePearsonCorrelation(x, y) {
    const n = x.length;
    if (n === 0) return 0;
    
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
    const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
    
    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    
    return denominator === 0 ? 0 : numerator / denominator;
}

// 將相關矩陣轉換為熱力圖格式
function convertToHeatmapFormat(matrix, labels) {
    const heatmapData = [];
    
    for (let i = 0; i < labels.length; i++) {
        for (let j = 0; j < labels.length; j++) {
            heatmapData.push({
                x: labels[j],
                y: labels[i],
                v: matrix[i][j]
            });
        }
    }
    
    return heatmapData;
}

// 生成全作業標籤頻率統計圖表（包含所有評論）
export async function generateHwLabelChart() {
    try {
        console.log('開始載入3標籤資料...');
        
        // 載入3標籤資料
        const response = await fetch('../output/final_result.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        console.log('計算標籤頻率統計（包含所有評論）...');
        const stats = calculateHwLabelFrequency(data);
        console.log('標籤頻率統計結果:', stats);
        
        // 創建圖表
        const chart = createHwLabelChart('hwLabelChart', stats, '全作業3標籤出現頻率統計（包含所有評論）');
        
        // 顯示統計摘要
        displayHwStatsSummary(stats, '所有評論');
        
        return chart;
    } catch (error) {
        console.error('生成全作業標籤頻率圖表時發生錯誤:', error);
        return null;
    }
}

// 生成全作業標籤頻率統計圖表（僅統計有標籤評論）
export async function generateHwEnableLabelChart() {
    try {
        console.log('開始載入3標籤資料...');
        
        // 載入3標籤資料
        const response = await fetch('../output/final_result.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('資料載入成功，共有作業:', Object.keys(data));
        
        console.log('計算標籤頻率統計（僅統計有標籤評論）...');
        const stats = calculateHwEnableLabelFrequency(data);
        console.log('標籤頻率統計結果（僅有標籤）:', stats);
        
        // 檢查統計結果是否為空
        const hasValidData = Object.keys(stats).length > 0 && 
                           Object.values(stats).some(hw => hw.total > 0);
        
        if (!hasValidData) {
            console.warn('警告：沒有找到有效的標籤數據');
            return null;
        }
        
        // 檢查畫布是否存在
        const canvas = document.getElementById('hwLabelValidChart');
        if (!canvas) {
            console.error('錯誤：找不到hwLabelValidChart畫布元素');
            return null;
        }
        console.log('✓ 畫布元素確認存在');
        
        // 創建圖表
        console.log('開始創建圖表...');
        const chart = createHwLabelChart('hwLabelValidChart', stats, '全作業3標籤出現頻率統計（僅統計有標籤評論）');
        
        if (chart) {
            console.log('✓ 圖表創建成功');
        } else {
            console.log('✗ 圖表創建失敗');
        }
        
        // 顯示統計摘要
        displayHwStatsSummary(stats, '有標籤評論');
        
        return chart;
    } catch (error) {
        console.error('生成全作業標籤頻率圖表（僅有標籤）時發生錯誤:', error);
        console.error('錯誤堆疊:', error.stack);
        return null;
    }
}

// 計算每個作業的3標籤出現頻率（包含所有評論）
export function calculateHwLabelFrequency(data) {
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
                    // 只統計有完整資料且有非空白評論的回合
                    if (round.Relevance !== undefined && 
                        round.Concreteness !== undefined && 
                        round.Constructive !== undefined &&
                        round.Feedback && round.Feedback.trim() !== '') {
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

// 計算每個作業的3標籤出現頻率（僅統計有標籤的評論）
export function calculateHwEnableLabelFrequency(data) {
    console.log('開始計算有效評論標籤頻率...');
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
    
    console.log('初始化統計結構:', Object.keys(hwStats));
    
    // 統計每個作業的標籤頻率（僅包含有標籤的評論）
    Object.entries(data).forEach(([hwName, hwData]) => {
        console.log(`處理作業 ${hwName}，學生數量: ${hwData.length}`);
        let validCommentsInHw = 0;
        
        hwData.forEach((student, studentIndex) => {
            if (student.Round && Array.isArray(student.Round)) {
                student.Round.forEach((round, roundIndex) => {
                    // 只統計有完整資料、有非空白評論且至少有一個標籤的回合
                    if (round.Relevance !== undefined && 
                        round.Concreteness !== undefined && 
                        round.Constructive !== undefined &&
                        round.Feedback && round.Feedback.trim() !== '') {
                        
                        const hasAnyLabel = round.Relevance === 1 || round.Concreteness === 1 || round.Constructive === 1;
                        
                        if (hasAnyLabel) {
                            validCommentsInHw++;
                            hwStats[hwName].total++;
                            if (round.Relevance === 1) hwStats[hwName].relevance++;
                            if (round.Concreteness === 1) hwStats[hwName].concreteness++;
                            if (round.Constructive === 1) hwStats[hwName].constructive++;
                        }
                    }
                });
            }
        });
        
        console.log(`${hwName} 有效評論數: ${validCommentsInHw}`);
    });
    
    console.log('原始統計結果:', hwStats);
    
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
    
    console.log('百分比統計結果:', percentageStats);
    
    return percentageStats;
}

// 創建全作業標籤頻率圖表（使用Canvas API）
export function createHwLabelChart(canvasId, stats, title = '全作業3標籤出現頻率統計') {
    console.log(`開始創建圖表，canvasId: ${canvasId}, title: ${title}`);
    console.log('統計數據:', stats);
    
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`找不到 canvas 元素: ${canvasId}`);
        return null;
    }
    
    console.log(`✓ 找到畫布元素: ${canvasId}`);
    console.log(`畫布尺寸: ${canvas.width}x${canvas.height}`);
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('無法獲取2D渲染上下文');
        return null;
    }
    
    const dpr = window.devicePixelRatio || 1;
    console.log(`設備像素比: ${dpr}`);
    
    // 動態設置canvas尺寸
    const container = canvas.parentElement;
    const containerWidth = container.clientWidth - 40; // 減去padding
    const containerHeight = 500; // 固定高度
    
    console.log(`容器尺寸: ${containerWidth}x${containerHeight}`);
    
    // 設置canvas顯示尺寸
    canvas.style.width = containerWidth + 'px';
    canvas.style.height = containerHeight + 'px';
    
    // 設置canvas實際尺寸（考慮DPI）
    canvas.width = containerWidth * dpr;
    canvas.height = containerHeight * dpr;
    ctx.scale(dpr, dpr);
    
    // 啟用抗鋸齒
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    
    // 準備資料
    const hwNames = Object.keys(stats).sort();
    const relevanceData = hwNames.map(hw => stats[hw].relevance);
    const concretenessData = hwNames.map(hw => stats[hw].concreteness);
    const constructiveData = hwNames.map(hw => stats[hw].constructive);
    
    console.log(`作業數量: ${hwNames.length}`, { hwNames, relevanceData, concretenessData, constructiveData });
    
    // 圖表尺寸和邊距
    const chartWidth = containerWidth;
    const chartHeight = containerHeight;
    const margin = { top: 80, right: 60, bottom: 100, left: 80 };
    const plotWidth = chartWidth - margin.left - margin.right;
    const plotHeight = chartHeight - margin.top - margin.bottom;
    
    // 清空畫布
    ctx.clearRect(0, 0, chartWidth, chartHeight);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, chartWidth, chartHeight);
    
    // 繪製標題
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(title, chartWidth / 2, 30);
    
    // 計算柱狀圖參數
    const barGroupWidth = plotWidth / hwNames.length * 0.7; // 減少寬度比例，增加間距
    const barSpacing = plotWidth / hwNames.length * 0.3;
    const individualBarWidth = barGroupWidth / 3;
    
    // 確保最小柱寬
    const minBarWidth = 20;
    const actualBarWidth = Math.max(individualBarWidth, minBarWidth);
    
    // 顏色配置
    const colors = {
        relevance: 'rgba(255, 206, 84, 0.8)',
        concreteness: '#B3EC94',
        constructive: 'rgba(153, 102, 255, 0.8)'
    };
    
    // 繪製Y軸
    ctx.strokeStyle = '#666666';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(margin.left, margin.top);
    ctx.lineTo(margin.left, margin.top + plotHeight);
    ctx.stroke();
    
    // 繪製X軸
    ctx.beginPath();
    ctx.moveTo(margin.left, margin.top + plotHeight);
    ctx.lineTo(margin.left + plotWidth, margin.top + plotHeight);
    ctx.stroke();
    
    // 繪製Y軸標籤和刻度
    ctx.fillStyle = '#666666';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    
    for (let i = 0; i <= 10; i++) {
        const y = margin.top + plotHeight - (i * plotHeight / 10);
        const value = i * 10;
        
        // 刻度線
        ctx.strokeStyle = i === 0 ? '#666666' : '#eeeeee';
        ctx.beginPath();
        ctx.moveTo(margin.left - 5, y);
        ctx.lineTo(margin.left + plotWidth, y);
        ctx.stroke();
        
        // 標籤
        ctx.fillText(value + '%', margin.left - 10, y + 4);
    }
    
    // 繪製Y軸標題
    ctx.save();
    ctx.translate(20, margin.top + plotHeight / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('出現頻率 (%)', 0, 0);
    ctx.restore();
    
    // 繪製柱狀圖
    hwNames.forEach((hwName, index) => {
        const groupX = margin.left + index * (plotWidth / hwNames.length) + barSpacing / 2;
        
        // Relevance柱
        const relevanceHeight = (relevanceData[index] / 100) * plotHeight;
        ctx.fillStyle = colors.relevance;
        ctx.fillRect(groupX, margin.top + plotHeight - relevanceHeight, actualBarWidth, relevanceHeight);
        
        // Concreteness柱
        const concretenessHeight = (concretenessData[index] / 100) * plotHeight;
        ctx.fillStyle = colors.concreteness;
        ctx.fillRect(groupX + actualBarWidth, margin.top + plotHeight - concretenessHeight, actualBarWidth, concretenessHeight);
        
        // Constructive柱
        const constructiveHeight = (constructiveData[index] / 100) * plotHeight;
        ctx.fillStyle = colors.constructive;
        ctx.fillRect(groupX + actualBarWidth * 2, margin.top + plotHeight - constructiveHeight, actualBarWidth, constructiveHeight);
        
        // X軸標籤
        ctx.fillStyle = '#666666';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(hwName, groupX + barGroupWidth / 2, margin.top + plotHeight + 20);
    });
    
    // 繪製X軸標題
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('作業名稱', chartWidth / 2, chartHeight - 40);
    
    // 繪製圖例
    const legendY = chartHeight - 70;
    const legendItems = [
        { label: 'Relevance', color: colors.relevance },
        { label: 'Concreteness', color: colors.concreteness },
        { label: 'Constructive', color: colors.constructive }
    ];
    
    const legendItemWidth = 150;
    const totalLegendWidth = legendItems.length * legendItemWidth;
    const legendStartX = (chartWidth - totalLegendWidth) / 2;
    
    legendItems.forEach((item, index) => {
        const x = legendStartX + index * legendItemWidth;
        
        // 圖例色塊
        ctx.fillStyle = item.color;
        ctx.fillRect(x, legendY, 15, 15);
        
        // 圖例文字
        ctx.fillStyle = '#333333';
        ctx.font = '14px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(item.label, x + 20, legendY + 12);
    });
    
    console.log(`圖表 ${canvasId} 繪製完成`);
    
    return {
        canvas: canvas,
        toBase64Image: function(format = 'image/png', quality = 1.0) {
            return canvas.toDataURL(format, quality);
        }
    };
}

// 保存圖表為PNG
export function saveChartAsPNG(chart, filename = 'hwLabelChart.png') {
    if (!chart) {
        console.error('圖表物件無效');
        return;
    }
    
    const link = document.createElement('a');
    link.download = filename;
    link.href = chart.toBase64Image('image/png', 1.0);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    console.log(`圖表已下載: ${filename}`);
}

// 顯示統計摘要
export function displayHwStatsSummary(stats, type = '所有評論') {
    console.log(`\n=== 全作業標籤頻率統計摘要（${type}）===`);
    console.log('作業\t\tRelevance (%)\tConcreteness (%)\tConstructive (%)\t總評論數');
    console.log('---'.repeat(25));
    
    Object.entries(stats).sort().forEach(([hwName, data]) => {
        console.log(`${hwName}\t\t${data.relevance.toFixed(1)}%\t\t${data.concreteness.toFixed(1)}%\t\t${data.constructive.toFixed(1)}%\t\t${data.total}`);
    });
}

// 創建HTML容器來顯示圖表（如果需要的話）
function createHwLabelChartContainer() {
    // 檢查是否已存在容器
    let container = document.getElementById('hw-label-chart-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'hw-label-chart-container';
        container.innerHTML = `
            <div style="margin: 20px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="text-align: center; margin-bottom: 20px;">全作業3標籤出現頻率統計</h3>
                <canvas id="hwLabelChart" width="800" height="600"></canvas>
                <div style="text-align: center; margin-top: 15px;">
                    <button id="downloadHwChart" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        下載圖表 PNG
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(container);
        
        // 添加下載按鈕事件
        document.getElementById('downloadHwChart').addEventListener('click', async () => {
            const chart = await generateHwLabelChart();
            if (chart) {
                saveChartAsPNG(chart, 'hwLabelChart.png');
            }
        });
    }
    
    return container;
}