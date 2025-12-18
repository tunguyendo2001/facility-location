package com.retaildss.repository;

import com.retaildss.entity.PotentialSite;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface PotentialSiteRepository extends JpaRepository<PotentialSite, Long> {
    
    /**
     * Lấy tất cả địa điểm đang ACTIVE
     */
    List<PotentialSite> findByStatusOrderByRankPositionAsc(String status);
    
    /**
     * Lấy top N địa điểm tốt nhất (đã có điểm TOPSIS)
     */
    @Query("SELECT ps FROM PotentialSite ps WHERE ps.status = 'ACTIVE' AND ps.topsisScore IS NOT NULL ORDER BY ps.rankPosition ASC")
    List<PotentialSite> findTopSites();
}

