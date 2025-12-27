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
@Table(name = "teachers")
public class Teacher {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "teacher_id", unique = true, nullable = false)
    private String teacherId; // 教工号

    @Column(name = "person_id", unique = true, nullable = false)
    private String personId; // 关联到 Person

    @Column
    private String department;

    // TODO: Roles stored as comma-separated string or separate table?
    // For simplicity, let's use comma-separated string for now, or use @ElementCollection
    // In Python code: roles: List[str]
    @Column
    private String roles; // e.g., "math,science"

    @Column(name = "account_id")
    private String accountId; // 绑定的账号ID

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
