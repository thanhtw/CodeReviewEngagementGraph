import { revelanceGraph } from "./graph_3labelFunc.js";

document.addEventListener("DOMContentLoaded", function () {
    fetch("../function/3labeled_processed_totalData.json")
        .then(response => response.json())
        .then(rawData => {
            console.log("原始資料範例：", rawData.HW4?.[0]);
            try {
                // 直接呼叫 generateGraph，資料處理已整合在函式內部
                revelanceGraph(rawData);
            }
            catch (err) {
                console.error("處理資料發生錯誤:", err);
            }
        })
        .catch(error => {
            console.error("讀取 JSON 失敗:", error);
        });
});

