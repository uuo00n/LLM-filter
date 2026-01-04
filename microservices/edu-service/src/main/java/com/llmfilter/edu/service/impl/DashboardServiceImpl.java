package com.llmfilter.edu.service.impl;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.llmfilter.edu.dto.*;
import com.llmfilter.edu.model.*;
import com.llmfilter.edu.repository.*;
import com.llmfilter.edu.security.UserContext;
import com.llmfilter.edu.service.DashboardService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class DashboardServiceImpl implements DashboardService {

    private final StudentRepository studentRepository;
    private final TeacherRepository teacherRepository;
    private final ScheduleRepository scheduleRepository;
    private final ObjectMapper objectMapper;
    
    private int getWeekday() {
        return LocalDate.now().getDayOfWeek().getValue();
    }

    private Map<Integer, String> getWeekDates() {
        LocalDate today = LocalDate.now();
        LocalDate monday = today.with(java.time.DayOfWeek.MONDAY);
        Map<Integer, String> weekDates = new HashMap<>();
        for (int i = 1; i <= 7; i++) {
            weekDates.put(i, monday.plusDays(i - 1).format(DateTimeFormatter.ISO_DATE));
        }
        return weekDates;
    }

    private String getLocationFromClassesJson(String classesJson, String targetClassId) {
        if (classesJson == null || targetClassId == null) return "未知地点";
        try {
            List<Map<String, Object>> classes = objectMapper.readValue(classesJson, new TypeReference<List<Map<String, Object>>>(){});
            for (Map<String, Object> cls : classes) {
                if (targetClassId.equals(cls.get("class_id"))) {
                    return (String) cls.getOrDefault("location", "未知地点");
                }
            }
        } catch (Exception e) {
            log.error("Failed to parse classes json: {}", classesJson, e);
        }
        return "未知地点";
    }

    @Override
    @Cacheable(value = "student_today_summary", key = "#user.personId + '_' + T(java.time.LocalDate).now().toString()", unless = "#result == null")
    public StudentTodaySummary getStudentTodaySummary(UserContext user) {
        String personId = user.getPersonId();
        if (personId == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "未绑定学生");
        }

        Student student = studentRepository.findByPersonId(personId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "未找到学生档案"));

        String classId = student.getClazz() != null ? student.getClazz().getClassId() : null;
        
        List<StudentTodaySummary.TodayScheduleItem> schedules = new ArrayList<>();
        if (classId != null) {
            int weekday = getWeekday();
            List<Schedule> dailySchedules = scheduleRepository.findByWeekdayAndClassIdOrderByPeriodAsc(weekday, classId);
            
            for (Schedule s : dailySchedules) {
                String location = getLocationFromClassesJson(s.getClassesJson(), classId);
                schedules.add(StudentTodaySummary.TodayScheduleItem.builder()
                        .lessonId(s.getLessonId())
                        .period(s.getPeriod())
                        .courseName(s.getCourseName())
                        .location(location)
                        .build());
            }
        }

        return StudentTodaySummary.builder()
                .student(StudentTodaySummary.StudentInfo.builder()
                        .studentId(student.getStudentId())
                        .name(student.getName())
                        .classId(classId)
                        .build())
                .todaySchedule(schedules)
                .todayAttendance(new ArrayList<>())
                .todayConduct(StudentTodaySummary.TodayConduct.builder().build())
                .build();
    }

    @Override
    public StudentWeekSummary getStudentWeekSchedule(UserContext user, Integer week) {
        String personId = user.getPersonId();
        if (personId == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "未绑定学生");
        }

        Student student = studentRepository.findByPersonId(personId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "未找到学生档案"));

        String classId = student.getClazz() != null ? student.getClazz().getClassId() : null;
        Map<String, List<StudentWeekSummary.WeekScheduleItem>> weekScheduleMap = new HashMap<>();
        
        // Initialize map for 1-5 (Mon-Fri) or 1-7
        for (int i = 1; i <= 7; i++) {
            weekScheduleMap.put(String.valueOf(i), new ArrayList<>());
        }

        if (classId != null) {
            List<Schedule> allSchedules = scheduleRepository.findByClassIdOrderByWeekdayAscPeriodAsc(classId);
            for (Schedule s : allSchedules) {
                String location = getLocationFromClassesJson(s.getClassesJson(), classId);
                StudentWeekSummary.WeekScheduleItem item = StudentWeekSummary.WeekScheduleItem.builder()
                        .lessonId(s.getLessonId())
                        .period(s.getPeriod())
                        .courseName(s.getCourseName())
                        .location(location)
                        .teacherPersonId(s.getTeacherPersonId())
                        .build();
                
                String dayKey = String.valueOf(s.getWeekday());
                if (weekScheduleMap.containsKey(dayKey)) {
                    weekScheduleMap.get(dayKey).add(item);
                }
            }
        }

        return StudentWeekSummary.builder()
                .currentWeek(week != null ? week : 1) // Default to week 1 if not provided
                .student(StudentWeekSummary.StudentInfo.builder()
                        .studentId(student.getStudentId())
                        .name(student.getName())
                        .classId(classId)
                        .build())
                .schedule(weekScheduleMap)
                .weekDates(getWeekDates())
                .build();
    }

    @Override
    public TeacherWeekSummary getTeacherWeekSchedule(UserContext user, Integer week) {
        String personId = user.getPersonId();
        if (personId == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "未绑定教师");
        }

        Teacher teacher = teacherRepository.findByPersonId(personId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "未找到教师档案"));

        Map<String, List<TeacherWeekSummary.WeekScheduleItem>> weekScheduleMap = new HashMap<>();
        for (int i = 1; i <= 7; i++) {
            weekScheduleMap.put(String.valueOf(i), new ArrayList<>());
        }

        List<Schedule> allSchedules = scheduleRepository.findByTeacherPersonIdOrderByWeekdayAscPeriodAsc(personId);
        for (Schedule s : allSchedules) {
            // 解析 classesJson 获取所有班级名称和地点
            List<TeacherWeekSummary.ClassInfo> classInfos = new ArrayList<>();
            try {
                if (s.getClassesJson() != null) {
                    List<Map<String, Object>> classes = objectMapper.readValue(s.getClassesJson(), new TypeReference<List<Map<String, Object>>>(){});
                    for (Map<String, Object> cls : classes) {
                        classInfos.add(TeacherWeekSummary.ClassInfo.builder()
                                .classId((String) cls.getOrDefault("class_id", ""))
                                .location((String) cls.getOrDefault("location", ""))
                                .build());
                    }
                }
            } catch (Exception e) {
                log.error("Failed to parse classes json for teacher schedule", e);
            }

            TeacherWeekSummary.WeekScheduleItem item = TeacherWeekSummary.WeekScheduleItem.builder()
                    .lessonId(s.getLessonId())
                    .period(s.getPeriod())
                    .courseName(s.getCourseName())
                    .classes(classInfos)
                    .build();

            String dayKey = String.valueOf(s.getWeekday());
            if (weekScheduleMap.containsKey(dayKey)) {
                weekScheduleMap.get(dayKey).add(item);
            }
        }

        return TeacherWeekSummary.builder()
                .currentWeek(week != null ? week : 1)
                .teacher(TeacherWeekSummary.TeacherInfo.builder()
                        .teacherId(teacher.getTeacherId())
                        .name("Unknown") // Name logic might need adjustment if not in Teacher table
                        .personId(teacher.getPersonId())
                        .build())
                .schedule(weekScheduleMap)
                .weekDates(getWeekDates())
                .build();
    }


    @Override
    public HomeroomCurrentSummary getHomeroomCurrentSummary(UserContext user) {
        return HomeroomCurrentSummary.builder().build();
    }

    @Override
    public DepartmentOverview getDepartmentOverview(UserContext user) {
        return DepartmentOverview.builder().build();
    }

    @Override
    public CampusOverview getCampusOverview(UserContext user) {
        return CampusOverview.builder().build();
    }
}
