import Papa from "papaparse";

export async function loadCSV(filePath) {
    try {
        const response = await fetch(filePath);
        const csvString = await response.text();
        const parsedData = Papa.parse(csvString, { header: true, dynamicTyping: true }).data;
        return parsedData; // 回傳解析後的資料
    } catch (error) {
        console.error("Error loading CSV:", error);
        return [];
    }
}