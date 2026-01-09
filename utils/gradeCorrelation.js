class GradeAnalyzer {
  constructor() {
    this.gradeData = null;
    this.labelData = null;
  }

  // 加載 CSV 文件
  async loadCSV(url) {
    const response = await fetch(url);
    const text = await response.text();
    return this.parseCSV(text);
  }

  // 解析 CSV
  parseCSV(csvText) {
    const rows = csvText.split('\n');
    const headers = rows[0].split(',');
    return rows.slice(1).map(row => {
      const values = row.split(',');
      return headers.reduce((obj, header, i) => {
        obj[header.trim()] = values[i]?.trim();
        return obj;
      }, {});
    });
  }

  // 加載 JSON 文件
  async loadJSON(url) {
    const response = await fetch(url);
    return response.json();
  }

  // 計算描述性統計
  calculateStats() {
    const labelCounts = {
      relevance: 0,
      concreteness: 0,
      constructive: 0
    };

    this.labelData.forEach(comment => {
      if (comment.labels.relevance) labelCounts.relevance++;
      if (comment.labels.concreteness) labelCounts.concreteness++;
      if (comment.labels.constructive) labelCounts.constructive++;
    });

    return labelCounts;
  }

  // 計算成績與標籤相關性
  calculateCorrelations() {
    const gradeMap = new Map(
      this.gradeData.map(student => [
        student['學號'], 
        parseFloat(student['總成績'])
      ])
    );

    const labelScores = {
      relevance: [],
      concreteness: [],
      constructive: []
    };

    this.labelData.forEach(comment => {
      const grade = gradeMap.get(comment.studentId);
      if (!grade) return;

      labelScores.relevance.push(comment.labels.relevance ? grade : null);
      labelScores.concreteness.push(comment.labels.concreteness ? grade : null);
      labelScores.constructive.push(comment.labels.constructive ? grade : null);
    });

    const correlations = {};
    Object.entries(labelScores).forEach(([label, grades]) => {
      const validGrades = grades.filter(g => g !== null);
      if (validGrades.length < 2) {
        correlations[label] = 0;
        return;
      }
      correlations[label] = this.pearsonCorrelation(validGrades);
    });

    return correlations;
  }

  // 皮爾森相關係數計算
  pearsonCorrelation(grades) {
    const n = grades.length;
    const sumX = grades.reduce((a, b) => a + b, 0);
    const sumY = n; // 假設標籤存在時為1
    const sumXY = grades.reduce((a, b) => a + b, 0);
    const sumX2 = grades.reduce((a, b) => a + b * b, 0);
    const sumY2 = n;

    const numerator = sumXY - (sumX * sumY) / n;
    const denominator = Math.sqrt(
      (sumX2 - (sumX * sumX) / n) * (sumY2 - (sumY * sumY) / n)
    );

    return denominator === 0 ? 0 : numerator / denominator;
  }

  // 初始化分析
  async init() {
    try {
      this.gradeData = await this.loadCSV('data/1111-物件導向設計實習_甲_期末成績.csv');
      this.labelData = await this.loadJSON('data/3labeled_processed_totalData.json');
      
      const stats = this.calculateStats();
      const correlations = this.calculateCorrelations();
      
      return { stats, correlations };
    } catch (error) {
      console.error('分析失敗:', error);
      return null;
    }
  }
}
