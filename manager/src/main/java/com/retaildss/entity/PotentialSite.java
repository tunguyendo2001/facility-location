package com.retaildss.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "potential_site")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PotentialSite {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "site_code", unique = true, length = 50)
    private String siteCode;
    
    @Column(nullable = false, length = 500)
    private String address;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "district_id", nullable = false)
    private District district;
    
    @Column(name = "x_coordinate")
    private Double xCoordinate;
    
    @Column(name = "y_coordinate")
    private Double yCoordinate;
    
    // Cost criteria
    @Column(name = "rent_cost", nullable = false)
    private Double rentCost;
    
    @Column(name = "renovation_cost", nullable = false)
    private Double renovationCost;
    
    @Column(name = "competitor_count", nullable = false)
    private Integer competitorCount;
    
    @Column(name = "distance_to_warehouse", nullable = false)
    private Double distanceToWarehouse;
    
    // Benefit criteria
    @Column(name = "floor_area", nullable = false)
    private Double floorArea;
    
    @Column(name = "front_width", nullable = false)
    private Double frontWidth;
    
    @Column(name = "traffic_score", nullable = false)
    private Integer trafficScore;
    
    @Column(name = "population_density", nullable = false)
    private Double populationDensity;
    
    // Additional attributes
    @Column(name = "has_parking")
    private Boolean hasParking = false;
    
    @Column(name = "is_corner_lot")
    private Boolean isCornerLot = false;
    
    @Column(name = "near_school")
    private Boolean nearSchool = false;
    
    @Column(name = "near_market")
    private Boolean nearMarket = false;
    
    // Metadata
    @Column(length = 20)
    private String status = "ACTIVE";
    
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(columnDefinition = "TEXT")
    private String notes;
    
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
