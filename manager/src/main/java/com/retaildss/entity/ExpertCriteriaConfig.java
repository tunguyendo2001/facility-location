package com.retaildss.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "expert_criteria_config")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExpertCriteriaConfig {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "strategy_name", nullable = false)
    private String strategyName;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    // Cost weights
    @Column(name = "weight_rent_cost", nullable = false)
    private Double weightRentCost;
    
    @Column(name = "weight_renovation_cost", nullable = false)
    private Double weightRenovationCost;
    
    @Column(name = "weight_competitor_count", nullable = false)
    private Double weightCompetitorCount;
    
    @Column(name = "weight_warehouse_distance", nullable = false)
    private Double weightWarehouseDistance;
    
    // Benefit weights
    @Column(name = "weight_floor_area", nullable = false)
    private Double weightFloorArea;
    
    @Column(name = "weight_front_width", nullable = false)
    private Double weightFrontWidth;
    
    @Column(name = "weight_traffic_score", nullable = false)
    private Double weightTrafficScore;
    
    @Column(name = "weight_population_density", nullable = false)
    private Double weightPopulationDensity;
    
    @Column(name = "is_active")
    private Boolean isActive = false;
    
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(name = "created_by")
    private String createdBy;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
