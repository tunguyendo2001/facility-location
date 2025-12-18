package com.retaildss.repository;

import com.retaildss.entity.ExpertCriteriaConfig;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface ExpertCriteriaConfigRepository extends JpaRepository<ExpertCriteriaConfig, Long> {
    
    /**
     * Lấy cấu hình trọng số đang được kích hoạt
     */
    Optional<ExpertCriteriaConfig> findByIsActiveTrue();
}
