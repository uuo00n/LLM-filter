package com.llmfilter.edu.dto;

import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class ScheduleDto {
    private String lessonId;
    private Integer weekday;
    private Integer period;
    private String courseName;
    private String teacherPersonId;
    private List<Map<String, Object>> classes;
}
