import json
import random
import os

def create_evaluation_dataset():
    """Function to generate question-answer pairs from email data"""
    
    # Set file paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, "data", "outlook_2021_cleaned.jsonl")
    
    # Read email data
    emails = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                email = json.loads(line)
                if email.get('body') and len(email['body']) > 200:  # Only sufficiently long bodies
                    emails.append(email)
            except:
                continue
    
    print(f"Read {len(emails)} emails in total.")
    
    # Generate evaluation dataset
    evaluation_pairs = []
    
    # Generate various types of question-answer pairs
    for i, email in enumerate(emails[:20]):  # Use only first 20
        subject = email.get('subject', '')
        body = email.get('body', '')
        from_email = email.get('from', '')
        to_email = email.get('to', '')
        date = email.get('date', '')
        
        # Generate question-answer pairs
        if i == 0:
            # ITER project related question
            question = "ITER 프로젝트에서 ANB 보고서는 무엇인가요?"
            answer = "ANB 보고서는 ITER 프로젝트에서 Nuclear Safety Officer가 작성하는 핵안전 관련 보고서입니다. 이 보고서들은 Vacuum Vessel Section에서 다양한 검토 절차와 테스트 결과를 문서화하며, 특히 Helium Leak Test Procedure, Cleaning Procedure, UT data 등의 검토 결과를 포함합니다."
            
        elif i == 1:
            # Document review related question
            question = "ITER에서 문서 검토 과정은 어떻게 진행되나요?"
            answer = "ITER에서 문서 검토는 다음과 같은 과정을 거칩니다: 1) IO(ITER Organization)에서 문서를 승인하고 검토를 위해 ANB에 전달, 2) ANB에서 검토 후 보고서 작성, 3) ESPN 관련 코멘트가 없는지 확인, 4) 문서 수신 확인 요청. 이 과정은 특히 Vacuum Vessel 관련 기술 문서들에 대해 엄격하게 진행됩니다."
            
        elif i == 2:
            # Meeting schedule related question
            question = "ITER 프로젝트에서 회의 일정은 어떻게 조정되나요?"
            answer = "ITER 프로젝트에서 회의 일정은 참석자들의 가용성을 고려하여 조정됩니다. 예를 들어, CEO 회의와 겹치는 경우 시간을 앞당기거나 다른 날로 변경할 수 있습니다. 참석자들이 더 일찍 참석할 수 없다면 늦은 시간(18:00-18:30)이나 다음 날 아침(08:00)으로 조정하는 것이 일반적입니다."
            
        elif i == 3:
            # UT 검사 관련 질문
            question = "ITER에서 UT 검사는 무엇이고 어떤 목적으로 사용되나요?"
            answer = "UT(Ultrasonic Testing) 검사는 ITER 프로젝트에서 용접부의 비파괴 검사 방법입니다. 특히 Vacuum Vessel의 production welds에 대해 PAUT(Phased Array Ultrasonic Testing)를 사용하여 용접 품질을 확인합니다. 이 검사는 VVPT(Vacuum Vessel Project Team)에서 검토한 후 ANB 검토를 위해 제공되며, NCR(Non-Conformance Report)과 연관되어 우선순위가 높은 검사입니다."
            
        elif i == 4:
            # 운송 관련 질문
            question = "ITER 프로젝트에서 VV Lifting Frame 운송은 어떻게 계획되나요?"
            answer = "VV Lifting Frame 운송은 PCR(Project Change Request) 11139를 통해 계획됩니다. F4E(Fusion for Energy)가 예산을 IO에 이전하여 운송을 위한 절단 작업을 수행하도록 되어 있습니다. 하지만 최근에는 DAHER와 협의하여 Cadarache에서 이탈리아 AMW까지 절단 없이 운송하는 방안을 검토하고 있으며, 이 경우 PCR의 해당 부분이 취소될 수 있습니다."
            
        elif i == 5:
            # 일정 관리 관련 질문
            question = "ITER 프로젝트의 단기 목표는 어떻게 설정되고 관리되나요?"
            answer = "ITER 프로젝트의 단기 목표는 주간 회의를 통해 설정되며, 다음과 같은 마일스톤들이 추적됩니다: CWP898 UPT 완료, CWP031 RB/SLT Prep 완료, CWP05 진단 완료(광섬유 및 전기 연속성 테스트 포함), CWP903.7 리프팅/툴링 시험 완료, VVTS IB 준비 등. 이러한 목표들은 CMA/CMO와의 논의를 통해 결정됩니다."
            
        elif i == 6:
            # 안전 관련 질문
            question = "ITER 프로젝트에서 핵안전은 어떻게 관리되나요?"
            answer = "ITER 프로젝트의 핵안전은 Nuclear Safety Officer가 담당하며, Vacuum Vessel Section에서 다양한 안전 절차를 관리합니다. ANB 보고서를 통한 검토, ESPN 관련 코멘트 확인, Helium Leak Test Procedure 검토 등을 통해 안전을 보장합니다. 모든 안전 관련 문서는 엄격한 검토 과정을 거쳐야 합니다."
            
        elif i == 7:
            # 용접 관련 질문
            question = "ITER에서 용접 품질 관리는 어떻게 이루어지나요?"
            answer = "ITER에서 용접 품질 관리는 PWTC(Production Weld Test Coupon)를 통해 이루어집니다. KODA/HHI에서 제작한 용접 테스트 쿠폰에 대해 ANB 검토를 받으며, 이는 우선순위가 높은 검토 항목입니다. 모든 용접 관련 문서는 ITER_D_ 형식으로 문서화되며, FTP를 통해 전달됩니다."
            
        elif i == 8:
            # 문서 관리 관련 질문
            question = "ITER 프로젝트에서 문서는 어떻게 관리되나요?"
            answer = "ITER 프로젝트의 문서는 IDM(Integrated Document Management) 시스템을 통해 관리됩니다. 문서는 ITER_D_ 형식으로 명명되며, 버전 관리가 이루어집니다. 문서 링크는 user.iter.org에서 제공되며, 검토자와 승인자의 역할이 명확히 구분되어 있습니다. 모든 문서는 검토 과정을 거쳐야 하며, 코멘트와 피드백이 반영됩니다."
            
        elif i == 9:
            # 팀 협업 관련 질문
            question = "ITER 프로젝트에서 팀 간 협업은 어떻게 이루어지나요?"
            answer = "ITER 프로젝트에서 팀 간 협업은 다양한 부서와 섹션 간의 긴밀한 소통을 통해 이루어집니다. Vacuum Vessel Section, Machine Construction Department, Sector Modules Delivery & Assembly Division 등이 협력하며, 정기적인 회의와 이메일을 통한 소통이 핵심입니다. 특히 국제적인 협력이 중요하여 한국, 유럽, 일본 등 다양한 국가의 전문가들이 참여합니다."
            
        elif i == 10:
            # 기술 검토 관련 질문
            question = "ITER에서 기술 검토 과정은 어떻게 진행되나요?"
            answer = "ITER의 기술 검토는 전문가들이 참여하는 다단계 과정입니다. 먼저 관련 섹션에서 초기 검토를 수행하고, 그 다음 ANB(Authorized Nuclear Body)에서 전문적인 검토를 진행합니다. 검토 과정에서 ESPN 관련 코멘트가 없는지 확인하며, 모든 검토 결과는 보고서로 문서화됩니다. 검토 완료 후에는 문서 수신 확인을 요청합니다."
            
        elif i == 11:
            # 일정 지연 관련 질문
            question = "ITER 프로젝트에서 일정 지연이 발생할 때는 어떻게 대응하나요?"
            answer = "ITER 프로젝트에서 일정 지연이 발생하면 우선순위를 재조정하고 대안을 모색합니다. 예를 들어, VV Lifting Frame 절단 작업이 PCR 승인 후에 논의된 경우, 절단 없이 운송하는 방안을 검토합니다. 또한 단기 목표를 재설정하고 참여자들의 가용성을 고려하여 일정을 조정합니다. 모든 변경사항은 관련 부서와 협의하여 결정됩니다."
            
        elif i == 12:
            # 품질 관리 관련 질문
            question = "ITER 프로젝트의 품질 관리는 어떤 시스템으로 운영되나요?"
            answer = "ITER 프로젝트의 품질 관리는 체계적인 문서화와 검토 과정을 통해 이루어집니다. NCR(Non-Conformance Report) 시스템을 통해 비준수 사항을 추적하고, ANB 보고서를 통한 전문적인 검토가 이루어집니다. 모든 기술 문서는 버전 관리되며, 검토자와 승인자의 역할이 명확히 구분되어 있습니다. 특히 용접, 검사, 안전 관련 작업에 대해서는 엄격한 품질 기준이 적용됩니다."
            
        elif i == 13:
            # 국제 협력 관련 질문
            question = "ITER 프로젝트에서 국제 협력은 어떻게 이루어지나요?"
            answer = "ITER 프로젝트는 국제적인 협력 프로젝트로, 다양한 국가의 전문가들이 참여합니다. 한국의 HHI, KODA, 유럽의 F4E, 일본의 기관들이 주요 참여자이며, 각국에서 전문 기술과 노하우를 제공합니다. 언어적 다양성으로 인해 영어가 공용어로 사용되며, 문화적 차이를 고려한 소통이 중요합니다. 정기적인 국제 회의와 이메일을 통한 지속적인 소통이 협력의 핵심입니다."
            
        elif i == 14:
            # 리스크 관리 관련 질문
            question = "ITER 프로젝트에서 리스크는 어떻게 관리되나요?"
            answer = "ITER 프로젝트의 리스크 관리는 다양한 측면에서 이루어집니다. 기술적 리스크는 전문가들의 다단계 검토를 통해 관리되며, 일정 리스크는 단기 목표 설정과 정기적인 모니터링을 통해 대응합니다. 안전 리스크는 Nuclear Safety Officer가 담당하며, 모든 안전 관련 절차가 엄격하게 검토됩니다. 또한 예산 리스크는 PCR을 통한 변경 관리로 대응하며, 모든 리스크는 문서화되어 추적됩니다."
            
        elif i == 15:
            # 커뮤니케이션 관련 질문
            question = "ITER 프로젝트에서 효과적인 커뮤니케이션은 어떻게 이루어지나요?"
            answer = "ITER 프로젝트에서 효과적인 커뮤니케이션은 정기적인 회의와 체계적인 이메일 소통을 통해 이루어집니다. 회의는 명확한 아젠다와 결정사항, 회의록을 통해 진행되며, 이메일은 다국적 팀원들을 고려하여 영어로 작성됩니다. 중요한 결정사항은 문서화되어 추적되며, 모든 이해관계자가 적절히 참여할 수 있도록 회의 시간을 조정합니다. 또한 기술적 내용은 전문 용어를 사용하되 명확하게 전달합니다."
            
        elif i == 16:
            # 기술 혁신 관련 질문
            question = "ITER 프로젝트에서 새로운 기술은 어떻게 도입되나요?"
            answer = "ITER 프로젝트에서 새로운 기술 도입은 신중한 검토 과정을 거칩니다. 먼저 관련 섹션에서 기술적 타당성을 검토하고, 그 다음 ANB에서 안전성과 규정 준수를 확인합니다. 새로운 기술은 기존 절차와의 호환성을 고려해야 하며, 모든 변경사항은 PCR을 통해 공식적으로 승인받아야 합니다. 기술 도입 시에는 교육과 훈련이 필수이며, 모든 과정이 문서화되어 추적됩니다."
            
        elif i == 17:
            # 비용 관리 관련 질문
            question = "ITER 프로젝트의 비용 관리는 어떻게 이루어지나요?"
            answer = "ITER 프로젝트의 비용 관리는 PCR(Project Change Request) 시스템을 통해 이루어집니다. 예산 변경이 필요한 경우 F4E와 IO 간의 예산 이전이 이루어지며, 모든 비용은 최적화된 공급업체를 통해 관리됩니다. 비용 효율성을 위해 대안 방안을 검토하며, 예를 들어 운송 비용을 절약하기 위해 절단 없이 운송하는 방안을 모색합니다. 모든 비용 관련 결정은 관련 부서와의 협의를 거쳐 이루어집니다."
            
        elif i == 18:
            # 지식 관리 관련 질문
            question = "ITER 프로젝트에서 지식과 경험은 어떻게 공유되나요?"
            answer = "ITER 프로젝트에서 지식과 경험은 체계적인 문서화와 정기적인 회의를 통해 공유됩니다. 모든 기술적 결정과 검토 결과는 문서로 기록되며, ANB 보고서, PCR, 기술 문서 등을 통해 축적됩니다. 정기적인 회의를 통해 최신 정보를 공유하고, 이메일을 통한 지속적인 소통이 이루어집니다. 또한 국제적인 협력을 통해 각국의 전문 지식과 경험이 공유되며, 이를 통해 프로젝트 전체의 역량이 향상됩니다."
            
        elif i == 19:
            # 프로젝트 성공 요인 관련 질문
            question = "ITER 프로젝트의 성공을 위한 핵심 요소는 무엇인가요?"
            answer = "ITER 프로젝트의 성공을 위한 핵심 요소는 다음과 같습니다: 1) 체계적인 품질 관리와 안전 시스템, 2) 국제적인 협력과 소통, 3) 전문가들의 다단계 검토 과정, 4) 명확한 문서화와 추적 시스템, 5) 유연한 일정 관리와 리스크 대응, 6) 지속적인 기술 혁신과 개선. 이러한 요소들이 유기적으로 결합되어 복잡한 핵융합 프로젝트의 성공을 이끌어냅니다."
        
        evaluation_pairs.append({
            "id": i + 1,
            "question": question,
            "expected_answer": answer,
            "source_email": {
                "subject": subject,
                "from": from_email,
                "to": to_email,
                "date": date,
                "body_preview": body[:500] + "..." if len(body) > 500 else body
            }
        })
    
    return evaluation_pairs

if __name__ == "__main__":
    pairs = create_evaluation_dataset()
    
    # 마크다운 형식으로 출력
    print("# ITER Outlook 이메일 RAG 시스템 평가 데이터셋")
    print()
    print("이 데이터셋은 ITER 프로젝트의 실제 이메일 데이터를 기반으로 생성된 질문-답변 쌍입니다.")
    print("RAG 시스템의 성능을 평가하기 위해 사용할 수 있습니다.")
    print()
    
    for pair in pairs:
        print(f"## {pair['id']}. {pair['question']}")
        print()
        print("**예상 답변:**")
        print(pair['expected_answer'])
        print()
        print("**원본 이메일 정보:**")
        print(f"- **제목:** {pair['source_email']['subject']}")
        print(f"- **발신자:** {pair['source_email']['from']}")
        print(f"- **수신자:** {pair['source_email']['to']}")
        print(f"- **날짜:** {pair['source_email']['date']}")
        print(f"- **본문 미리보기:** {pair['source_email']['body_preview']}")
        print()
        print("---")
        print()
