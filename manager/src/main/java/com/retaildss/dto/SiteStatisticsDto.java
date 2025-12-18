package com.retaildss.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SiteStatisticsDto {
    private Long totalSites;
    private Long activeSites;
    private Long analyzedSites;
    private Double averageTopsisScore;
    private Double averageRentCost;
}
