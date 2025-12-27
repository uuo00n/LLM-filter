package com.llmfilter.edu.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import javax.persistence.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "schedules")
public class Schedule {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "lesson_id", unique = true, nullable = false)
    private String lessonId;

    @Column(nullable = false)
    private Integer weekday; // 1-7

    @Column(nullable = false)
    private Integer period; // 1-8

    @Column(name = "course_name")
    private String courseName;

    @Column(name = "teacher_person_id")
    private String teacherPersonId; // 关联到 Teacher.personId

    // 存储班级信息的 JSON 字符串 (简化处理，实际生产建议用关联表)
    // Python code: classes: List[Dict[str, Any]]
    @Column(columnDefinition = "TEXT")
    private String classesJson; 

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
