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
public class TeacherWeekSummary {
    private TeacherInfo teacher;
    private Integer currentWeek;
    private Map<Integer, String> weekDates;
    private Map<String, List<WeekScheduleItem>> schedule;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TeacherInfo {
        private String teacherId;
        private String name;
        private String personId;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class WeekScheduleItem {
        private String lessonId;
        private Integer period;
        private String courseName;
        private List<ClassInfo> classes;
        private String startTime;
        private String endTime;
    }
    
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ClassInfo {
        private String classId;
        private String location;
    }
}
