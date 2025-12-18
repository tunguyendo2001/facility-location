package com.retaildss.service;

import com.retaildss.dto.SiteStatisticsDto;
import com.retaildss.dto.TopSiteDto;
import com.retaildss.entity.PotentialSite;
import com.retaildss.exception.ResourceNotFoundException;
import com.retaildss.repository.PotentialSiteRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional(readOnly = true)
public class SiteService {
    
    private final PotentialSiteRepository siteRepository;
    
    public List<PotentialSite> getAllActiveSites() {
        return siteRepository.findByStatusOrderByRankPositionAsc("ACTIVE");
    }
    
    public PotentialSite getSiteById(Long id) {
        return siteRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("PotentialSite", "id", id));
    }
    
    public List<TopSiteDto> getTopSites(int limit) {
        List<PotentialSite> sites = siteRepository.findTopSites();
        
        return sites.stream()
            .limit(limit)
            .map(site -> new TopSiteDto(
                site.getId(),
                site.getSiteCode(),
                site.getAddress(),
                site.getDistrict().getName(),
                site.getTopsisScore(),
                site.getRankPosition(),
                site.getRentCost(),
                site.getFloorArea(),
                site.getTrafficScore(),
                site.getCompetitorCount()
            ))
            .collect(Collectors.toList());
    }
    
    public SiteStatisticsDto getStatistics() {
        long totalSites = siteRepository.count();
        long activeSites = siteRepository.findByStatusOrderByRankPositionAsc("ACTIVE").size();
        
        List<PotentialSite> analyzedSites = siteRepository.findTopSites();
        
        Double avgTopsisScore = analyzedSites.stream()
            .filter(s -> s.getTopsisScore() != null)
            .mapToDouble(PotentialSite::getTopsisScore)
            .average()
            .orElse(0.0);
        
        Double avgRentCost = analyzedSites.stream()
            .mapToDouble(PotentialSite::getRentCost)
            .average()
            .orElse(0.0);
        
        return new SiteStatisticsDto(
            totalSites,
            activeSites,
            (long) analyzedSites.size(),
            avgTopsisScore,
            avgRentCost
        );
    }
}
