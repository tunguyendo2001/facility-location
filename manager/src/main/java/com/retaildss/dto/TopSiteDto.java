package com.retaildss.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TopSiteDto {
    private Long id;
    private String siteCode;
    private String address;
    private String districtName;
    private Double topsisScore;
    private Integer rankPosition;
    private Double rentCost;
    private Double floorArea;
    private Integer trafficScore;
    private Integer competitorCount;
}
