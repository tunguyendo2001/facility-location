package com.retaildss.repository;

import com.retaildss.entity.PotentialSite;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface PotentialSiteRepository extends JpaRepository<PotentialSite, Long> {

    /**
     * Lấy tất cả địa điểm theo trạng thái
     */
    List<PotentialSite> findByStatus(String status);
}
