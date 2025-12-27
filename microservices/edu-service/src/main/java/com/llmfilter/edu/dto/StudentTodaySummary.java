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
public class StudentTodaySummary {
    private StudentInfo student;
    private List<TodayScheduleItem> todaySchedule;
    private List<TodayAttendanceItem> todayAttendance;
    private TodayConduct todayConduct;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StudentInfo {
        private String studentId;
        private String name;
        private String classId;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TodayScheduleItem {
        private String lessonId;
        private Integer period;
        private String courseName;
        private String location;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TodayAttendanceItem {
        private String lessonId;
        private String status;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TodayConduct {
        private String date;
        private Map<String, Object> metrics;
        private String teacherComment;
        private String headTeacherComment;
        private Double score;
    }
}
