package com.llmfilter.edu.repository;

import com.llmfilter.edu.model.Schedule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ScheduleRepository extends JpaRepository<Schedule, Long> {
    Optional<Schedule> findByLessonId(String lessonId);
    List<Schedule> findAllByOrderByWeekdayAscPeriodAsc();
    
    // 注意：Schedule 实体中的 classes 字段是 JSONB 类型，直接查询可能需要原生 SQL
    // 这里暂时使用 Native Query 进行模拟，或者如果 Schedule 实体已正确映射，尝试使用 JPA 方法
    // 假设 Schedule 实体中没有直接关联 ClassEntity，而是通过 JSON 存储
    // 简化起见，我们先用原生 SQL 查（PostgreSQL JSONB 语法）
    // SELECT * FROM schedules s, jsonb_array_elements(s.classes) c WHERE c->>'class_id' = :classId AND s.weekday = :weekday ORDER BY s.period ASC
    
    // 为避免复杂的 SQL 编写，这里先定义方法签名，实现留给开发者或使用简单的全表过滤（不推荐但可行）
    // 或者假设 Schedule 实体通过中间表关联了 ClassEntity
    // 根据之前的 init_mongo.py，schedules 包含 classes: [{"class_id": "...", "location": "..."}]
    
    // 临时方案：使用 Native Query 查询 JSONB
    @org.springframework.data.jpa.repository.Query(value = "SELECT * FROM schedules s WHERE s.weekday = :weekday AND EXISTS (SELECT 1 FROM jsonb_array_elements(s.classes) c WHERE c->>'class_id' = :classId) ORDER BY s.period ASC", nativeQuery = true)
    List<Schedule> findByWeekdayAndClassIdOrderByPeriodAsc(Integer weekday, String classId);

    @org.springframework.data.jpa.repository.Query(value = "SELECT * FROM schedules s WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(s.classes) c WHERE c->>'class_id' = :classId) ORDER BY s.weekday ASC, s.period ASC", nativeQuery = true)
    List<Schedule> findByClassIdOrderByWeekdayAscPeriodAsc(String classId);

    List<Schedule> findByTeacherPersonIdAndWeekdayOrderByPeriodAsc(String teacherPersonId, Integer weekday);
    
    List<Schedule> findByTeacherPersonIdOrderByWeekdayAscPeriodAsc(String teacherPersonId);
}
