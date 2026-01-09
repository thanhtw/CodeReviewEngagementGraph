# Progedu_Review_Network

## 1. 讀取 totalData.json

## 2. 設計 dataOrganize.py，將資料重組為指定的格式

## 3. 產生 hw_2.json (hw_num.json)

# 打開html - open graph.html

// 建立一个新的空节点集合
var nodes = new vis.DataSet();
// 建立一个新的空边集合
var edges = new vis.DataSet();

// 建立一个存放review score的空集合
var reviewerScores = {};
let reviewerCounts = {};

// 遍历记录数据
recordData.forEach((record) => {
const reviewerId = record.reviewId; // 从记录中获取评论者 ID

    record.round.forEach((rnd) => {
      // 确保评论者 ID 已经在对象中有对应的键
      if (!reviewerScores[reviewerId]) {
        reviewerScores[reviewerId] = 0; // 初始化评论者的分数为 0
        reviewerCounts[reviewerId] = 0;
      }
      // 将当前 round 的分数加到评论者的总分上
      reviewerScores[reviewerId] += rnd.reviewScore;
      reviewerCounts[reviewerId]++;
    });

});

let avgReviewScores = {};
for (let reviewerId in reviewerScores) {
if (reviewerCounts[reviewerId] > 0) {
// Ensure there's at least one valid score
avgReviewScores[reviewerId] =
reviewerScores[reviewerId] / reviewerCounts[reviewerId];
} else {
avgReviewScores[reviewerId] = 0; // Handle cases with no valid scores if necessary
}
}

// 找出最大字数
const maxWords = Math.max(
...recordData.flatMap((record) =>
record.round.map((rnd) => rnd.feedback.trim().length),
),
);
console.log(maxWords);

// 遍历每条记录,为每个交互创建节点和边
recordData.forEach((record) => {
const authorNodeId = `author-${record.authorUsername}`;
const reviewerNodeId = `reviewer-${record.reviewId}`;

    // 更新作者节点信息
    nodes.update({
      id: authorNodeId,
      label: record.authorName,
      value: getSizeByReviewScore(record.avgReviewScore), // assuming avgReviewScore is calculated and available
      color: { background: "#FFD7DE", border: "#FFC0CB" }, // 统一设置为粉红色
    });

    record.round.forEach((rnd) => {
      var isCommentEmpty =
        rnd.feedback.trim() === "" || rnd.feedback === "无回馈";
      var nodeSize = getSizeByReviewScore(avgReviewScores[reviewerNodeId]);

      // 计算正规化分数和对应的颜色,创建节点
      const normalizedScore = (rnd.feedback.trim().length / maxWords) * 100;
      const lightness = 80 - normalizedScore * 0.5; // 计算亮度,范围从90%到10%
      const nodeColor = `hsl(350, 100%, ${lightness}%)`;

      // 更新评论者节点信息,包括标签和大小
      nodes.update({
        id: reviewerNodeId,
        label: record.reviewerName,
        value: nodeSize,
        color: { background: nodeColor, border: nodeColor },
      });

      // 决定边的颜色
      let edgeColor = isCommentEmpty ? "red" : "#199FD8";
      if (rnd.status === 1) {
        const firstRound = record.round.find((r) => r.status === 3);
        if (firstRound && firstRound.score === 1) {
          edgeColor = "#3CE62D"; // 第一回合分数为1,第二回合设为绿色
        }
      }

      // 添加边,设置颜色和样式
      edges.add({
        from: reviewerNodeId,
        to: authorNodeId,
        arrows: "to",
        dashes: isCommentEmpty,
        color: edgeColor,
      });
    });

});

// 根据评分来确定节点大小的函数
function getSizeByReviewScore(avgReviewScore) {
if (avgReviewScore > 0 && avgReviewScore < 1) return 100;
if (avgReviewScore == 1) return 200;
if (avgReviewScore == 2) return 300;
if (avgReviewScore == 3) return 400;
if (avgReviewScore == 4) return 500;
return 10; // 其他情况默认为最小大小 10
}

// 获取容器元素,通常是一个div,用来展示网络图
var container = document.getElementById("reviewNetwork");
// 构造网络图所需的数据,包括节点和边
var data = {
nodes: nodes,
edges: edges,
};

var options = {
nodes: {
scaling: {
min: 10, // 节点大小的最小值为 10
max: 500, // 节点大小的最大值为 400
label: {
// 关于节点标签的配置
enabled: true, // 启用标签显示
min: 14, // 标签字体的最小大小为 14
max: 200, // 字體的最大大小为 200
maxVisible: 30, // 最大可见范围为 30 单位
drawThreshold: 5, // 绘制阈值为 5
},
customScalingFunction: function (min, max, total, value) {
// 自定义的节点大小调整函数,根据节点的值（value）决定其大小
if (value <= 10) return 0.1; // 預設值
if (value <= 100) return 0.15; // 如果值小于或等于 100,则大小比例为 0.25
if (value <= 200) return 0.2; // 如果值小于或等于 200,则大小比例为 0.5
if (value <= 300) return 0.25; // 如果值小于或等于 300,则大小比例为 0.75
if (value <= 400) return 0.3; // 如果值小于或等于 400,则大小比例为 1
return 0.35; // 如果值大于 400,大小比例为 1
},
},
},
};

// 创建一个新的 network,并将其附加到容器上
var network = new vis.Network(container, data, options);
