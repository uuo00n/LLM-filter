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
public class DepartmentOverview {
    private StudentsAttendance studentsAttendance;
    private List<TeacherRate> teacherAttendanceRates;
    private List<AnomalyClass> anomalies;
    private List<DirectiveInfo> directives;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StudentsAttendance {
        private Long total;
        private Long present;
        private Long absentOrLeave;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TeacherRate {
        private String teacherId;
        private Integer presentSlots;
        private Integer totalSlots;
        private Double rate;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AnomalyClass {
        private String classId;
        private Double anomalyRate;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DirectiveInfo {
        private String level;
        private String content;
        private String createdAt;
    }
}
