package com.retaildss.service;

import com.retaildss.dto.TopSiteDto;
import com.retaildss.entity.EvaluationResult;
import com.retaildss.repository.EvaluationResultRepository;
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
public class EvaluationResultService {
    
    private final EvaluationResultRepository evaluationResultRepository;
    
    /**
     * Get top N sites from the latest analysis batch
     */
    public List<TopSiteDto> getTopSitesFromLatestBatch(int limit) {
        List<EvaluationResult> results = evaluationResultRepository.findTopResultsFromLatestBatch(limit);
        
        return results.stream()
            .map(er -> new TopSiteDto(
                er.getSite().getId(),
                er.getSite().getSiteCode(),
                er.getSite().getAddress(),
                er.getSite().getDistrict().getName(),
                er.getTopsisScore(),
                er.getRankPosition(),
                er.getSite().getRentCost(),
                er.getSite().getFloorArea(),
                er.getSite().getTrafficScore(),
                er.getSite().getCompetitorCount()
            ))
            .collect(Collectors.toList());
    }
    
    /**
     * Get latest evaluation result for each site
     */
    public List<EvaluationResult> getLatestEvaluationForEachSite() {
        return evaluationResultRepository.findLatestEvaluationForEachSite();
    }
    
    /**
     * Get evaluation history for a specific site
     */
    public List<EvaluationResult> getEvaluationHistoryBySite(Long siteId) {
        return evaluationResultRepository.findBySiteIdOrderByCreatedAtDesc(siteId);
    }
    
    /**
     * Get all results from a specific batch
     */
    public List<EvaluationResult> getResultsByBatchId(String batchId) {
        return evaluationResultRepository.findByBatchIdOrderByRankPositionAsc(batchId);
    }
    
    /**
     * Get the latest batch ID
     */
    public String getLatestBatchId() {
        return evaluationResultRepository.findLatestBatchId();
    }
}
