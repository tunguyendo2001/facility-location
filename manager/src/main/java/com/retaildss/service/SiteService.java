package com.retaildss.service;

import com.retaildss.dto.SiteStatisticsDto;
import com.retaildss.dto.TopSiteDto;
import com.retaildss.entity.EvaluationResult;
import com.retaildss.entity.PotentialSite;
import com.retaildss.exception.ResourceNotFoundException;
import com.retaildss.repository.EvaluationResultRepository;
import com.retaildss.repository.PotentialSiteRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class SiteService {

    private final PotentialSiteRepository siteRepository;
    private final EvaluationResultRepository evaluationResultRepository;

    public List<PotentialSite> getAllActiveSites() {
        return siteRepository.findByStatus("ACTIVE");
    }

    public PotentialSite getSiteById(Long id) {
        return siteRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("PotentialSite", "id", id));
    }

    public List<TopSiteDto> getTopSites(int limit) {
        List<EvaluationResult> results = evaluationResultRepository.findTopResultsFromLatestBatch(limit);

        return results.stream()
                .map(res -> {
                    PotentialSite site = res.getSite();
                    return new TopSiteDto(
                            site.getId(),
                            site.getSiteCode(),
                            site.getAddress(),
                            site.getDistrict().getName(),
                            res.getTopsisScore(),
                            res.getRankPosition(),
                            site.getRentCost(),
                            site.getFloorArea(),
                            site.getTrafficScore(),
                            site.getCompetitorCount());
                })
                .collect(Collectors.toList());
    }

    public SiteStatisticsDto getStatistics() {
        long totalSites = siteRepository.count();
        long activeSites = siteRepository.findByStatus("ACTIVE").size();

        List<EvaluationResult> latestEvaluations = evaluationResultRepository.findLatestEvaluationForEachSite();

        Double avgTopsisScore = latestEvaluations.stream()
                .mapToDouble(EvaluationResult::getTopsisScore)
                .average()
                .orElse(0.0);

        Double avgRentCost = latestEvaluations.stream()
                .mapToDouble(er -> er.getSite().getRentCost())
                .average()
                .orElse(0.0);

        return new SiteStatisticsDto(
                totalSites,
                activeSites,
                (long) latestEvaluations.size(),
                avgTopsisScore,
                avgRentCost);
    }
}
