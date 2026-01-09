#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from collections import defaultdict
import re

def comprehensive_data_check():
    """
    全面檢查所有學生的相關性、具體性、建設性標籤資料
    """
    
    try:
        # 讀取處理後的資料
        with open('3labeled_processed_totalData.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("=== 學生資料全面檢查報告 ===\n")
        
        # 統計變數
        student_stats = defaultdict(lambda: {
            'total_assignments': 0,
            'total_rounds': 0,
            'total_feedbacks': 0,
            'valid_feedbacks': 0,
            'empty_feedbacks': 0,
            'relevance_count': 0,
            'concreteness_count': 0,
            'constructive_count': 0,
            'suggestion_keywords': 0,
            'anomalies': []
        })
        
        # 關鍵字檢查 - 只檢查真正的建議關鍵字
        suggestion_keywords = ['建議']
        
        total_rounds = 0
        total_assignments = 0
        
        # 遍歷所有作業和學生
        for hw_key, assignments in data.items():
            total_assignments += len(assignments)
            print(f"檢查 {hw_key}: {len(assignments)} 個 assignment")
            
            for assignment in assignments:
                reviewer = assignment.get('Reviewer_Name') or assignment.get('reviewer')
                if not reviewer:
                    continue
                
                student_stats[reviewer]['total_assignments'] += 1
                rounds = assignment.get('Round', [])
                
                for round_data in rounds:
                    total_rounds += 1
                    student_stats[reviewer]['total_rounds'] += 1
                    
                    feedback = round_data.get('Feedback', '')
                    relevance = round_data.get('Relevance', 0)
                    concreteness = round_data.get('Concreteness', 0)
                    constructive = round_data.get('Constructive', 0)
                    
                    student_stats[reviewer]['total_feedbacks'] += 1
                    
                    # 檢查評論內容
                    if feedback and str(feedback).strip():
                        student_stats[reviewer]['valid_feedbacks'] += 1
                        feedback_str = str(feedback)
                        
                        # 檢查關鍵字
                        for keyword in suggestion_keywords:
                            if keyword in feedback_str:
                                student_stats[reviewer]['suggestion_keywords'] += 1
                                break
                        
                        # 異常檢查1: 有建議關鍵字但建設性標籤為0
                        if any(keyword in feedback_str for keyword in suggestion_keywords) and constructive == 0:
                            student_stats[reviewer]['anomalies'].append({
                                'type': 'missing_constructive_for_suggestion',
                                'hw': hw_key,
                                'feedback': feedback_str[:100] + '...' if len(feedback_str) > 100 else feedback_str,
                                'labels': f'R:{relevance},C:{concreteness},Ct:{constructive}'
                            })
                        
                        # 異常檢查2: 非常短的評論但有多個標籤
                        if len(feedback_str.strip()) <= 5 and (relevance + concreteness + constructive) >= 2:
                            student_stats[reviewer]['anomalies'].append({
                                'type': 'short_feedback_multiple_labels',
                                'hw': hw_key,
                                'feedback': feedback_str,
                                'labels': f'R:{relevance},C:{concreteness},Ct:{constructive}'
                            })
                        
                        # 異常檢查3: 只說"good"但有具體性標籤
                        if feedback_str.strip().lower() in ['good', 'pass', '是', '是的', '讚', '棒'] and concreteness == 1:
                            student_stats[reviewer]['anomalies'].append({
                                'type': 'generic_feedback_with_concreteness',
                                'hw': hw_key,
                                'feedback': feedback_str,
                                'labels': f'R:{relevance},C:{concreteness},Ct:{constructive}'
                            })
                        
                        # 異常檢查4: 詳細評論但所有標籤都是0
                        if len(feedback_str.strip()) > 50 and relevance == 0 and concreteness == 0 and constructive == 0:
                            student_stats[reviewer]['anomalies'].append({
                                'type': 'detailed_feedback_no_labels',
                                'hw': hw_key,
                                'feedback': feedback_str[:100] + '...' if len(feedback_str) > 100 else feedback_str,
                                'labels': f'R:{relevance},C:{concreteness},Ct:{constructive}'
                            })
                    else:
                        student_stats[reviewer]['empty_feedbacks'] += 1
                        
                        # 異常檢查5: 空評論但有標籤
                        if relevance == 1 or concreteness == 1 or constructive == 1:
                            student_stats[reviewer]['anomalies'].append({
                                'type': 'empty_feedback_with_labels',
                                'hw': hw_key,
                                'feedback': '[空評論]',
                                'labels': f'R:{relevance},C:{concreteness},Ct:{constructive}'
                            })
                    
                    # 累計標籤統計
                    student_stats[reviewer]['relevance_count'] += relevance
                    student_stats[reviewer]['concreteness_count'] += concreteness
                    student_stats[reviewer]['constructive_count'] += constructive
        
        # 生成報告
        print(f"總計檢查: {len(student_stats)} 位學生, {total_assignments} 個 assignment, {total_rounds} 個 round\n")
        
        # 1. 整體統計
        print("=== 整體標籤分布 ===")
        total_relevance = sum(stats['relevance_count'] for stats in student_stats.values())
        total_concreteness = sum(stats['concreteness_count'] for stats in student_stats.values())
        total_constructive = sum(stats['constructive_count'] for stats in student_stats.values())
        total_valid_feedbacks = sum(stats['valid_feedbacks'] for stats in student_stats.values())
        
        print(f"相關性標籤: {total_relevance} ({total_relevance/total_rounds*100:.1f}%)")
        print(f"具體性標籤: {total_concreteness} ({total_concreteness/total_rounds*100:.1f}%)")
        print(f"建設性標籤: {total_constructive} ({total_constructive/total_rounds*100:.1f}%)")
        print(f"有效評論: {total_valid_feedbacks} ({total_valid_feedbacks/total_rounds*100:.1f}%)")
        
        # 2. 異常學生檢查
        print("\n=== 可能有問題的學生 ===")
        problem_students = []
        
        for student_id, stats in student_stats.items():
            problems = []
            
            # 檢查1: 完全沒有任何標籤
            if stats['relevance_count'] == 0 and stats['concreteness_count'] == 0 and stats['constructive_count'] == 0:
                if stats['valid_feedbacks'] > 0:
                    problems.append(f"有{stats['valid_feedbacks']}個有效評論但無任何標籤")
            
            # 檢查2: 標籤比例異常高
            if stats['valid_feedbacks'] > 0:
                rel_ratio = stats['relevance_count'] / stats['valid_feedbacks']
                con_ratio = stats['concreteness_count'] / stats['valid_feedbacks']
                cst_ratio = stats['constructive_count'] / stats['valid_feedbacks']
                
                if rel_ratio > 3:  # 相關性比例超過300%
                    problems.append(f"相關性比例異常高: {rel_ratio:.1%}")
                if con_ratio > 2:  # 具體性比例超過200%
                    problems.append(f"具體性比例異常高: {con_ratio:.1%}")
                if cst_ratio > 1.5:  # 建設性比例超過150%
                    problems.append(f"建設性比例異常高: {cst_ratio:.1%}")
            
            # 檢查3: 有建議關鍵字但建設性標籤很少
            if stats['suggestion_keywords'] > 0 and stats['constructive_count'] < stats['suggestion_keywords'] * 0.5:
                problems.append(f"有{stats['suggestion_keywords']}個建議關鍵字但建設性標籤只有{stats['constructive_count']}個")
            
            # 檢查4: 有多個異常記錄
            if len(stats['anomalies']) >= 3:
                problems.append(f"有{len(stats['anomalies'])}個異常記錄")
            
            if problems:
                problem_students.append({
                    'student': student_id,
                    'problems': problems,
                    'stats': stats
                })
        
        # 顯示前10個問題學生
        problem_students.sort(key=lambda x: len(x['problems']) + len(x['stats']['anomalies']), reverse=True)
        
        for i, student_info in enumerate(problem_students[:10]):
            student_id = student_info['student']
            problems = student_info['problems']
            stats = student_info['stats']
            
            print(f"\n{i+1}. 學生 {student_id}:")
            print(f"   統計: {stats['valid_feedbacks']}個有效評論, R:{stats['relevance_count']}, C:{stats['concreteness_count']}, Ct:{stats['constructive_count']}")
            
            for problem in problems:
                print(f"   ⚠️  {problem}")
            
            if stats['anomalies']:
                print(f"   異常記錄 ({len(stats['anomalies'])}個):")
                for anomaly in stats['anomalies'][:3]:  # 只顯示前3個
                    print(f"      - {anomaly['type']}: {anomaly['feedback']} [{anomaly['labels']}]")
        
        # 3. 異常類型統計
        print("\n=== 異常類型統計 ===")
        anomaly_types = defaultdict(int)
        for stats in student_stats.values():
            for anomaly in stats['anomalies']:
                anomaly_types[anomaly['type']] += 1
        
        for anomaly_type, count in sorted(anomaly_types.items(), key=lambda x: x[1], reverse=True):
            print(f"{anomaly_type}: {count} 個案例")
        
        # 4. 建議關鍵字檢查
        print("\n=== 建議關鍵字檢查 ===")
        total_suggestion_keywords = sum(stats['suggestion_keywords'] for stats in student_stats.values())
        print(f"總計找到 {total_suggestion_keywords} 個建議關鍵字")
        
        # 檢查建議關鍵字與建設性標籤的對應
        suggestion_constructive_mismatch = 0
        for stats in student_stats.values():
            for anomaly in stats['anomalies']:
                if anomaly['type'] == 'missing_constructive_for_suggestion':
                    suggestion_constructive_mismatch += 1
        
        print(f"有建議關鍵字但建設性標籤為0的案例: {suggestion_constructive_mismatch} 個")
        
        print(f"\n檢查完成！總共發現 {len(problem_students)} 位學生可能有資料問題。")
        
        return {
            'total_students': len(student_stats),
            'problem_students': len(problem_students),
            'total_anomalies': sum(len(stats['anomalies']) for stats in student_stats.values()),
            'student_stats': dict(student_stats)
        }
        
    except Exception as e:
        print(f"檢查過程中發生錯誤: {e}")
        return None

if __name__ == "__main__":
    comprehensive_data_check()
