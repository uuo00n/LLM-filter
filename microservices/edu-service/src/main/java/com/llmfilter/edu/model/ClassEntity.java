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
@Table(name = "classes")
public class ClassEntity implements java.io.Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "class_id", unique = true, nullable = false)
    private String classId; // 业务上的班级ID，如 "2023-01"

    @Column(nullable = false)
    private String name;

    @Column
    private String major;

    @Column(name = "head_teacher_person_id")
    private String headTeacherPersonId; // 班主任人物ID（指向 Teacher.personId）

    @Column(name = "grade")
    private Integer grade; // 年级

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
