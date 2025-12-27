package com.llmfilter.edu.dto;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HomeroomCurrentSummary {
    private List<CurrentLesson> currentLessons;
    private List<AttendanceRate> attendanceRates;
    private List<LeaveInfo> leaves;
    private List<DirectiveInfo> directives;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CurrentLesson {
        private String classId;
        private String courseName;
        private String location;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AttendanceRate {
        private String classId;
        private Long present;
        private Integer total;
        private Double rate;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LeaveInfo {
        private String studentId;
        private String classId;
        private String reason;
        private String status;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DirectiveInfo {
        private String content;
        private String createdAt;
    }
}
