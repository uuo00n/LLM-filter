package com.llmfilter.edu.dto;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CampusOverview {
    private Long totalStudents;
    private Long present;
    private Long leaves;
    private Long directives;
    private List<Map<String, Object>> termGoals;
    private List<Map<String, Object>> departmentProgress;
}
