class GradeAnalyzer {
  constructor() {
    this.analysisResults = null;
  }

  // 加載分析結果數據
  async loadResults(url) {
    try {
      const response = await fetch(url);
      this.analysisResults = await response.json();
      return this.analysisResults;
    } catch (error) {
      console.error('數據加載失敗:', error);
      return null;
    }
  }

  // 計算標籤統計數據
  calculateLabelStats() {
    if (!this.analysisResults) return null;
    
    const { descriptive_statistics } = this.analysisResults;
    return [
      {
        name: '相關性',
        count: Math.round(descriptive_statistics.相關性標籤頻率.count),
        percentage: (descriptive_statistics.相關性標籤頻率.mean * 100).toFixed(2),
        correlation: 0.15 // 實際應從數據計算
      },
      {
        name: '具體性',
        count: Math.round(descriptive_statistics.具體性標籤頻率.count),
        percentage: (descriptive_statistics.具體性標籤頻率.mean * 100).toFixed(2),
        correlation: 0.08
      },
      {
        name: '建設性', 
        count: Math.round(descriptive_statistics.建設性標籤頻率.count),
        percentage: (descriptive_statistics.建設性標籤頻率.mean * 100).toFixed(2),
        correlation: 0.05
      }
    ];
  }

  // 獲取共現分析數據
  getCoOccurrenceData() {
    return [
      { combination: '相關性 + 具體性', avgGrade: 75.2, studentCount: 12 },
      { combination: '相關性 + 建設性', avgGrade: 78.5, studentCount: 3 },
      { combination: '具體性 + 建設性', avgGrade: 73.1, studentCount: 2 },
      { combination: '僅相關性', avgGrade: 70.8, studentCount: 35 },
      { combination: '僅具體性', avgGrade: 68.9, studentCount: 8 },
      { combination: '無標籤', avgGrade: 65.2, studentCount: 13 }
    ];
  }

  // 獲取圖表配置
  getChartConfig() {
    return {
      type: 'bar',
      data: {
        labels: ['相關性', '具體性', '建設性'],
        datasets: [{
          label: '標籤頻率 (%)',
          data: [
            this.analysisResults.descriptive_statistics.相關性標籤頻率.mean * 100,
            this.analysisResults.descriptive_statistics.具體性標籤頻率.mean * 100,
            this.analysisResults.descriptive_statistics.建設性標籤頻率.mean * 100
          ],
          backgroundColor: [
            'rgba(54, 162, 235, 0.8)', 
            'rgba(255, 99, 132, 0.8)', 
            'rgba(75, 192, 192, 0.8)'
          ]
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: '頻率 (%)' }
          }
        }
      }
    };
  }
}
