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
public class StudentWeekSummary {
    private StudentInfo student;
    private Integer currentWeek;
    private Map<Integer, String> weekDates;
    private Map<String, List<WeekScheduleItem>> schedule;

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
    public static class WeekScheduleItem {
        private String lessonId;
        private Integer period;
        private String courseName;
        private String location;
        private String startTime;
        private String endTime;
        private String teacherPersonId;
    }
}
