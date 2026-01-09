let maxLengthAuthorName;
let maxAvgFeedbackLength;
document.addEventListener("DOMContentLoaded", function () {
  fetch("../utils/HW2.json") // 確保 JSON 文件路徑正確
      .then(response => {
          if (!response.ok) {
              throw new Error(`Network response was not ok: ${response.statusText}`);
          }
          return response.json();
      })
      .then(data => {
          console.log("Data loaded successfully:", data);
          
          // 確保載入資料後執行邏輯
          processDataAndDrawGraph(data);
      })
      .catch(error => {
          console.error("Error loading JSON:", error);
      });
});


function processDataAndDrawGraph(recordData) {
  // 確保資料是有效陣列
  if (!Array.isArray(recordData)) {
      console.error("Invalid data format:", recordData);
      return;
  }

  // 初始化節點和邊的集合
  const nodes = new vis.DataSet();
  const edges = new vis.DataSet();

  // 記錄 reviewer 的平均分數與數量
  const reviewerScores = {};
  const reviewerCounts = {};

  recordData.forEach(record => {
      const reviewerId = record.reviewerUsername;

      record.round.forEach(rnd => {
          if (!reviewerScores[reviewerId]) {
              reviewerScores[reviewerId] = 0;
              reviewerCounts[reviewerId] = 0;
          }
          reviewerScores[reviewerId] += rnd.reviewScore;
          reviewerCounts[reviewerId]++;
      });
  });

  const avgReviewScores = {};
  for (let reviewerId in reviewerScores) {
      avgReviewScores[reviewerId] = reviewerCounts[reviewerId] > 0
          ? reviewerScores[reviewerId] / reviewerCounts[reviewerId]
          : 0;
  }

  // 計算最大 AvgFeedbackLength
  const maxAvgFeedbackLength = Math.max(
      ...recordData.map(record => record.avgFeedbackLength)
  );

  console.log("Max AvgFeedbackLength:", maxAvgFeedbackLength);

  const top10Records = recordData
      .sort((a, b) => b.avgFeedbackLength - a.avgFeedbackLength)
      .slice(0, 10);

  console.log("Top 10 avgFeedbackLength Records:", top10Records);

  // 建立用戶節點
  const userNodes = {};
recordData.forEach(record => {
    const authorId = record.authorUsername;

    // 設置統一顏色
    const color = "#9ED5F4";  // 使用統一的顏色
    if (!userNodes[authorId]) {
        userNodes[authorId] = {
            id: authorId,
            label: record.authorName,
            value: 10,
            color: color,
        };
    }
});


  for (let userId in userNodes) {
      nodes.add(userNodes[userId]);
  }

  // 設置邊資料
  recordData.forEach(record => {
      const authorId = record.authorUsername;
      const reviewerId = record.reviewerUsername;

      record.round.forEach(rnd => {
          const isCommentEmpty = rnd.feedback.trim() === "" || rnd.feedback === "無回饋";

          let edgeColor = isCommentEmpty ? "red" : "#199FD8";
          let edgeWidth = edgeColor === "red" ? 4 : 1;

          edges.add({
              from: reviewerId,
              to: authorId,
              arrows: "to",
              dashes: isCommentEmpty,
              width: edgeWidth,
              color: edgeColor,
          });
      });
  });

  // 初始化網絡圖
  drawGraph(nodes, edges);
}

// 繪製網絡圖的函數
function drawGraph(nodes, edges) {
  const container = document.getElementById("reviewNetwork");
  const data = { nodes, edges };
  const options = {
      nodes: {
          scaling: {
              min: 30,
              max: 100,
          },
      },
      edges: {
          physics: true,
          length: 1000,
      },
      physics: {
          barnesHut: {
              gravitationalConstant: -2000,
              centralGravity: 0.3,
              springLength: 200,
          },
      },
  };

  const network = new vis.Network(container, data, options);
}
