/**
 * Bubble Chart Functionality
 * Each bubble represents a student. Y-axis shows label ratio, bubble size indicates review participation rate.
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
                        top: 80,
                        right: 40,
                        bottom: 80,
                        left: 80
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Multi-Dimensional Review Quality Matrix',
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
                                return context[0].raw.studentName || `Student ${context[0].dataIndex + 1}`;
                            },
                            label: function(context) {
                                const data = context.raw;
                                const labelNames = ['Relevance', 'Concreteness', 'Constructive', 'Overall'];
                                const labelName = labelNames[Math.round(data.x)];
                                const percentage = (data.labelRatio * 100).toFixed(1);
                                
                                const percentageText = data.labelType === 3 
                                    ? `${percentage}% (3-label average)` 
                                    : `${percentage}%${data.labelRatio > 1 ? ' (multi-label review)' : ''}`;
                                
                                return [
                                    `Quality Metric: ${labelName}`,
                                    `Label Ratio: ${percentageText}`,
                                    `Participation Rate: ${(data.reviewCompletionRate * 100).toFixed(1)}%`,
                                    `Valid Reviews: ${data.validRounds || data.validComments || 0}`,
                                    `Assigned Tasks: ${data.assignedTasks || 0}`
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
                            text: 'Quality Metrics'
                        },
                        min: -0.5,
                        max: 3.5,
                        ticks: {
                            stepSize: 1,
                            min: 0,
                            max: 3,
                            callback: function(value, index, values) {
                                const labels = ['Relevance', 'Concreteness', 'Constructive', 'Overall'];
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
                            text: 'Students'
                        },
                        min: -1.5,
                        max: 1.5,
                        ticks: {
                            stepSize: 1,
                            callback: function(value, index, values) {
                                const chart = Chart.getChart(this.ctx);
                                const roundedValue = Math.round(value);
                                if (chart && chart.studentNames && chart.studentNames[roundedValue] && roundedValue >= 0) {
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

        // Store current mode to chart object
        this.chart.currentMode = this.currentMode;
    }

    updateChart() {
        if (!this.data) {
            console.log('No data available for bubble chart');
            return;
        }

        const bubbleData = this.prepareBubbleData();
        
        // Create datasets for four quality indicators
        const datasets = [
            {
                label: 'Relevance',
                data: bubbleData.filter(d => d.labelType === 0),
                backgroundColor: bubbleData.filter(d => d.labelType === 0).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 0).map(d => d.borderColor),
                borderWidth: 2
            },
            {
                label: 'Concreteness',
                data: bubbleData.filter(d => d.labelType === 1),
                backgroundColor: bubbleData.filter(d => d.labelType === 1).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 1).map(d => d.borderColor),
                borderWidth: 2
            },
            {
                label: 'Constructive',
                data: bubbleData.filter(d => d.labelType === 2),
                backgroundColor: bubbleData.filter(d => d.labelType === 2).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 2).map(d => d.borderColor),
                borderWidth: 2
            },
            {
                label: 'Overall',
                data: bubbleData.filter(d => d.labelType === 3),
                backgroundColor: bubbleData.filter(d => d.labelType === 3).map(d => d.color),
                borderColor: bubbleData.filter(d => d.labelType === 3).map(d => d.borderColor),
                borderWidth: 2
            }
        ];

        this.chart.data.datasets = datasets;
        this.chart.options.plugins.title.text = 'Multi-Dimensional Review Quality Matrix';
        
        this.chart.update();
    }

    prepareBubbleData() {
        const students = this.extractStudentData();
        const bubbleData = [];
        const studentNames = [];

        console.log(`Preparing bubble chart data: ${students.length} students`);

        // Update Y-axis range
        this.chart.options.scales.y.min = -1.5;
        this.chart.options.scales.y.max = students.length + 0.5;
        
        // Create bubble data in sorted order (reversed Y-axis, best students at top)
        students.forEach((student, studentIndex) => {
            studentNames.push(student.name);
            
            // Review participation rate = Completed assignments / Assigned assignments
            const reviewCompletionRate = student.reviewCompletionRate;
            
            // Create bubbles for each quality indicator
            const labelTypes = [
                { type: 0, name: 'relevance', displayName: 'Relevance' },
                { type: 1, name: 'concreteness', displayName: 'Concreteness' },
                { type: 2, name: 'constructive', displayName: 'Constructive' },
                { type: 3, name: 'all', displayName: 'Overall' }
            ];
            
            labelTypes.forEach(labelInfo => {
                let labelRatio = 0;
                
                // Calculate label ratio
                if (labelInfo.type === 3) { // Overall mode - average of three label ratios
                    labelRatio = student.averageLabelRatio;
                } else {
                    // Single label ratio = label count / valid review rounds
                    const labelCount = student[`${labelInfo.name}Count`] || 0;
                    labelRatio = labelCount / Math.max((student.validRounds || student.validComments), 1);
                }
                
                // Bubble size: based on review participation rate, range 2px-25px
                const bubbleSize = Math.max(Math.min(reviewCompletionRate * 25, 15), 3);
                
                // Bubble color: based on label ratio
                const { color, borderColor } = this.getBubbleColorForLabel(labelRatio, labelInfo.type);
                
                bubbleData.push({
                    x: labelInfo.type,     // X-axis: Quality indicator (0=Relevance, 1=Concreteness, 2=Constructive, 3=Overall)
                    y: students.length - 1 - studentIndex,  // Y-axis: Reversed order, best students at top
                    r: bubbleSize,         // Bubble size: Review participation rate
                    studentName: student.name,
                    studentId: student.id,
                    labelType: labelInfo.type,
                    labelName: labelInfo.displayName,
                    labelRatio: labelRatio,
                    validComments: student.validComments,       // Completed assignments count
                    validRounds: student.validRounds,           // Valid rounds count (label ratio denominator)
                    assignedTasks: student.assignedTasks,
                    reviewCompletionRate: reviewCompletionRate,
                    relevanceCount: student.relevanceCount || 0,
                    concretenessCount: student.concretenessCount || 0,
                    constructiveCount: student.constructiveCount || 0,
                    color: color,
                    borderColor: borderColor
                });
            });
            
            // Debug: Show details for top 3 students
            if (studentIndex < 3) {
                const yPosition = students.length - 1 - studentIndex;
                console.log(`Top ${studentIndex + 1} student ${student.name} (Y-axis position: ${yPosition}):`, {
                    reviewCompletionRate: (reviewCompletionRate * 100).toFixed(1) + '%',
                    averageLabelRatio: (student.averageLabelRatio * 100).toFixed(1) + '%',
                    validComments: student.validComments,
                    validRounds: student.validRounds,
                    assignedTasks: student.assignedTasks,
                    relevanceCount: student.relevanceCount,
                    concretenessCount: student.concretenessCount,
                    constructiveCount: student.constructiveCount,
                    note: 'Students with largest bubbles shown at top'
                });
            }
        });
        
        // Store student names to chart object for Y-axis labels (reversed order)
        this.chart.studentNames = studentNames.reverse();
        
        console.log(`Bubble chart data ready: ${bubbleData.length} bubbles`);
        return bubbleData;
    }

    extractStudentData() {
        if (!this.data || !this.data.nodes) {
            return [];
        }

        const students = [];
        this.data.nodes.forEach(node => {
            if (node.group === 'student') {
                // Calculate review participation rate (bubble size)
                const reviewCompletionRate = (node.validComments || 0) / Math.max(node.assignedTasks || 1, 1);
                
                // Calculate total label ratio (color intensity)
                const validRoundsCount = Math.max((node.validRounds || node.validComments || 0), 1);
                const relevanceRatio = (node.relevanceCount || 0) / validRoundsCount;
                const concretenessRatio = (node.concretenessCount || 0) / validRoundsCount;
                const constructiveRatio = (node.constructiveCount || 0) / validRoundsCount;
                const averageLabelRatio = (relevanceRatio + concretenessRatio + constructiveRatio) / 3;
                
                students.push({
                    id: node.id,
                    name: node.label,
                    validComments: node.validComments || 0,
                    validRounds: node.validRounds || 0,
                    assignedTasks: node.assignedTasks || 0,
                    relevanceCount: node.relevanceCount || 0,
                    concretenessCount: node.concretenessCount || 0,
                    constructiveCount: node.constructiveCount || 0,
                    reviewCompletionRate: reviewCompletionRate,
                    averageLabelRatio: averageLabelRatio
                });
            }
        });

        // Sort: First by review participation rate (bubble size) descending, then by average label ratio (color) descending
        students.sort((a, b) => {
            // First sort by bubble size (large bubbles first/top)
            if (Math.abs(a.reviewCompletionRate - b.reviewCompletionRate) > 0.01) {
                return b.reviewCompletionRate - a.reviewCompletionRate;
            }
            // When bubble size is similar, sort by color intensity (dark first/top)
            return b.averageLabelRatio - a.averageLabelRatio;
        });

        console.log('Student sorting results (top 5):', students.slice(0, 5).map(s => ({
            name: s.name,
            reviewCompletionRate: (s.reviewCompletionRate * 100).toFixed(1) + '%',
            averageLabelRatio: (s.averageLabelRatio * 100).toFixed(1) + '%'
        })));

        return students;
    }

    getBubbleColorForLabel(labelRatio, labelType) {
        // 4-level color calculation
        // For overall mode (labelType=3), range is 0-100%
        // For single label mode (labelType=0,1,2), ratio may exceed 100% due to multi-label reviews
        let colorLevel;
        
        if (labelType === 3) {
            // Overall mode: 0-100% range
            if (labelRatio >= 0.75) colorLevel = 3;      // Darkest (75%+)
            else if (labelRatio >= 0.5) colorLevel = 2;  // Dark (50-75%)
            else if (labelRatio >= 0.25) colorLevel = 1; // Light (25-50%)
            else colorLevel = 0;                          // Lightest (<25%)
        } else {
            // Single label mode: 0-150%+ range (multi-label reviews possible)
            if (labelRatio >= 1.0) colorLevel = 3;       // Darkest (100%+)
            else if (labelRatio >= 0.67) colorLevel = 2; // Dark (67-100%)
            else if (labelRatio >= 0.33) colorLevel = 1; // Light (33-67%)
            else colorLevel = 0;                          // Lightest (<33%)
        }
        
        // Color config (consistent with node colors)
        const colorConfigs = [
            { // Relevance
                colors: ["rgba(255, 238, 183, 0.8)", "rgba(255, 215, 83, 0.8)", "rgba(241, 188, 13, 0.8)", "rgba(212, 163, 2, 0.8)"],
                borderColors: ["rgba(255, 238, 183, 1)", "rgba(255, 215, 83, 1)", "rgba(241, 188, 13, 1)", "rgba(212, 163, 2, 1)"]
            },
            { // Concreteness
                colors: ["rgba(207, 255, 202, 0.8)", "rgba(149, 237, 101, 0.8)", "rgba(84, 175, 35, 0.8)", "rgba(50, 113, 17, 0.8)"],
                borderColors: ["rgba(207, 255, 202, 1)", "rgba(149, 237, 101, 1)", "rgba(84, 175, 35, 1)", "rgba(50, 113, 17, 1)"]
            },
            { // Constructive
                colors: ["rgba(241, 220, 255, 0.8)", "rgba(199, 142, 237, 0.8)", "rgba(148, 68, 202, 0.8)", "rgba(89, 10, 142, 0.8)"],
                borderColors: ["rgba(241, 220, 255, 1)", "rgba(199, 142, 237, 1)", "rgba(148, 68, 202, 1)", "rgba(89, 10, 142, 1)"]
            },
            { // Overall
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
        // Remove existing modal if any
        const existingModal = document.querySelector('.student-detail-modal');
        if (existingModal) {
            document.body.removeChild(existingModal);
        }
        
        // Calculate label rates
        const validReviews = studentData.validRounds || studentData.validComments || 0;
        const relevanceRate = validReviews > 0 ? (studentData.relevanceCount / validReviews * 100).toFixed(1) : 0;
        const concretenessRate = validReviews > 0 ? (studentData.concretenessCount / validReviews * 100).toFixed(1) : 0;
        const constructiveRate = validReviews > 0 ? (studentData.constructiveCount / validReviews * 100).toFixed(1) : 0;
        const participationRate = studentData.reviewCompletionRate || 0;
        
        const modal = document.createElement('div');
        modal.className = 'student-detail-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${studentData.studentName || `Student ${studentData.studentId}`}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="modal-section">
                        <div class="section-title">📊 Review Statistics</div>
                        <div class="detail-row">
                            <span class="detail-label">Valid Reviews:</span>
                            <span class="detail-value">${validReviews}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Completed Tasks:</span>
                            <span class="detail-value">${studentData.validComments || 0}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Assigned Tasks:</span>
                            <span class="detail-value">${studentData.assignedTasks || 0}</span>
                        </div>
                        <div class="detail-row highlight">
                            <span class="detail-label">Participation Rate:</span>
                            <span class="detail-value rate-badge ${participationRate >= 0.8 ? 'rate-high' : participationRate >= 0.5 ? 'rate-medium' : 'rate-low'}">${(participationRate * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                    
                    <div class="modal-section">
                        <div class="section-title">🏷️ Quality Labels</div>
                        <div class="detail-row">
                            <span class="detail-label">
                                <span class="label-dot relevance"></span>
                                Relevance:
                            </span>
                            <span class="detail-value">${studentData.relevanceCount || 0} <span class="rate-text">(${relevanceRate}%)</span></span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">
                                <span class="label-dot concreteness"></span>
                                Concreteness:
                            </span>
                            <span class="detail-value">${studentData.concretenessCount || 0} <span class="rate-text">(${concretenessRate}%)</span></span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">
                                <span class="label-dot constructive"></span>
                                Constructive:
                            </span>
                            <span class="detail-value">${studentData.constructiveCount || 0} <span class="rate-text">(${constructiveRate}%)</span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close modal event
        const closeBtn = modal.querySelector('.modal-close');
        const closeModal = () => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        };
        
        closeBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        // ESC key to close
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

// Export for other modules
window.BubbleChartManager = BubbleChartManager;
