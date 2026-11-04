> SOFTWARE FIXTURE ONLY. No real model inference or Buddhist semantic judgment.

# BCR — AI semantic proposal (không phải phê duyệt học thuật)

    MODEL_INFERENCE_NOT_EXECUTED

## Mệnh đề được kiểm tra

    {
      "claim_id": "c",
      "text": "Only under condition T, the fixture describes a blue lamp.",
      "claim_type": "textual"
    }

## Nguồn đã kiểm — thông tin kiểm bằng chương trình

    {
      "current_checks": {
        "e-c99c36cfbfd9750d97fb1026": "VERIFIED"
      },
      "provenance": [
        {
          "evidence_id": "e-c99c36cfbfd9750d97fb1026",
          "corpus": "suttacentral-bilara",
          "repository": "suttacentral/bilara-data",
          "source_sha": "d4d4f16980291903b9f6f0d28648d388984f3549",
          "source_blob_sha": "23923eb3a757fcfd9f86c2450424754ff06cd75b",
          "source_path": "root/pli/ms/sutta/mn/mn1_root-pli-ms.json",
          "work_id": "mn1",
          "segment_id": "mn1:1.1",
          "sequence_no": 0,
          "witness": "root:root-pli-ms",
          "language": "pli",
          "text_role": "root_text",
          "evidence_class": "canonical_root"
        }
      ]
    }

## AI đánh giá — proposal

    {
      "claim_id": "c",
      "assessment_status": "PROPOSED",
      "support_level": "DIRECT",
      "supporting_evidence_ids": [
        "e-c99c36cfbfd9750d97fb1026"
      ],
      "considered_evidence_ids": [
        "e-c99c36cfbfd9750d97fb1026"
      ],
      "reasoning": [
        {
          "evidence_id": "e-c99c36cfbfd9750d97fb1026",
          "quote": "The first fixture passage describes a blue lamp.",
          "explanation": "Software fixture rationale, not semantic ground truth."
        }
      ],
      "scope_limits": [
        "Only under the supplied temporal/causal conditions."
      ],
      "missing_evidence": [],
      "unresolved_questions": [],
      "provenance": [
        {
          "evidence_id": "e-c99c36cfbfd9750d97fb1026",
          "corpus": "suttacentral-bilara",
          "repository": "suttacentral/bilara-data",
          "source_sha": "d4d4f16980291903b9f6f0d28648d388984f3549",
          "source_blob_sha": "23923eb3a757fcfd9f86c2450424754ff06cd75b",
          "source_path": "root/pli/ms/sutta/mn/mn1_root-pli-ms.json",
          "work_id": "mn1",
          "segment_id": "mn1:1.1",
          "sequence_no": 0,
          "witness": "root:root-pli-ms",
          "language": "pli",
          "text_role": "root_text",
          "evidence_class": "canonical_root"
        }
      ],
      "semantic_approval": false,
      "publication_authorized": false
    }

## AI phản biện — proposal riêng

    {
      "claim_id": "c",
      "assessment_status": "PROPOSED",
      "support_level": "WEAK",
      "supporting_evidence_ids": [
        "e-c99c36cfbfd9750d97fb1026"
      ],
      "considered_evidence_ids": [
        "e-c99c36cfbfd9750d97fb1026"
      ],
      "reasoning": [
        {
          "evidence_id": "e-c99c36cfbfd9750d97fb1026",
          "quote": "The first fixture passage describes a blue lamp.",
          "explanation": "Software fixture rationale, not semantic ground truth."
        }
      ],
      "scope_limits": [
        "Retain the explicit exception and time condition."
      ],
      "missing_evidence": [],
      "unresolved_questions": [],
      "action": "LOWER",
      "counter_evidence_ids": [],
      "issues": [],
      "provenance": [
        {
          "evidence_id": "e-c99c36cfbfd9750d97fb1026",
          "corpus": "suttacentral-bilara",
          "repository": "suttacentral/bilara-data",
          "source_sha": "d4d4f16980291903b9f6f0d28648d388984f3549",
          "source_blob_sha": "23923eb3a757fcfd9f86c2450424754ff06cd75b",
          "source_path": "root/pli/ms/sutta/mn/mn1_root-pli-ms.json",
          "work_id": "mn1",
          "segment_id": "mn1:1.1",
          "sequence_no": 0,
          "witness": "root:root-pli-ms",
          "language": "pli",
          "text_role": "root_text",
          "evidence_class": "canonical_root"
        }
      ],
      "semantic_approval": false,
      "publication_authorized": false
    }

## Kết luận giới hạn — luôn đọc cùng phạm vi bên dưới

    {
      "label": "Đề xuất hỗ trợ một phần/có điều kiện",
      "assessment_status": "PROPOSED",
      "support_level": "WEAK",
      "supporting_evidence_ids": [
        "e-c99c36cfbfd9750d97fb1026"
      ],
      "counter_evidence_ids": []
    }

## Phạm vi và điều kiện bắt buộc

    [
      "Condition T must remain.",
      "Only the resolved contiguous source text is verified; markup/escaped text is not flattened.",
      "AI proposal only; not authorized academic approval.",
      "Source independence is not established; translations do not count as independent witnesses.",
      "Only supplied pinned evidence/context and executed search scope were examined.",
      "Only under the supplied temporal/causal conditions.",
      "Retain the explicit exception and time condition."
    ]

## Việc cần kiểm tra thêm

    {
      "missing": [],
      "questions": [],
      "issues": [],
      "errors": []
    }

## Trạng thái

    {
      "semantic_approval": false,
      "publication_authorized": false,
      "source_independence": "NOT_ESTABLISHED",
      "independent_source_count": null
    }

HUMAN_ADJUDICATION_PENDING · DISTRIBUTION_CLEARED = 0 · PUBLICATION_NOT_PERMITTED
