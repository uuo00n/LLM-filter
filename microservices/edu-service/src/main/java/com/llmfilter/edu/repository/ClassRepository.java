package com.llmfilter.edu.repository;

import com.llmfilter.edu.model.ClassEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ClassRepository extends JpaRepository<ClassEntity, Long> {
    Optional<ClassEntity> findByClassId(String classId);
}
