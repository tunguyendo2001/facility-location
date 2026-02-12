package com.retaildss.repository;

import com.retaildss.entity.EvaluationResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface EvaluationResultRepository extends JpaRepository<EvaluationResult, Long> {
    
    /**
     * Lấy kết quả phân tích của một batch theo thứ tự rank
     */
    @Query("SELECT er FROM EvaluationResult er WHERE er.batchId = :batchId ORDER BY er.rankPosition ASC")
    List<EvaluationResult> findByBatchIdOrderByRankPositionAsc(@Param("batchId") String batchId);
    
    /**
     * Lấy batch_id mới nhất
     */
    @Query(value = "SELECT batch_id FROM evaluation_result ORDER BY created_at DESC LIMIT 1", nativeQuery = true)
    String findLatestBatchId();
    
    /**
     * Lấy top N kết quả của batch mới nhất
     */
    @Query(value = """
        SELECT er.* FROM evaluation_result er
        WHERE er.batch_id = (SELECT batch_id FROM evaluation_result ORDER BY created_at DESC LIMIT 1)
        ORDER BY er.rank_position ASC
        LIMIT :limit
        """, nativeQuery = true)
    List<EvaluationResult> findTopResultsFromLatestBatch(@Param("limit") int limit);
    
    /**
     * Lấy kết quả mới nhất cho từng site
     */
    @Query(value = """
        SELECT er.* FROM evaluation_result er
        INNER JOIN (
            SELECT site_id, MAX(created_at) as max_date
            FROM evaluation_result
            GROUP BY site_id
        ) latest ON er.site_id = latest.site_id AND er.created_at = latest.max_date
        ORDER BY er.topsis_score DESC
        """, nativeQuery = true)
    List<EvaluationResult> findLatestEvaluationForEachSite();
    
    /**
     * Lấy lịch sử đánh giá của một site
     */
    @Query("SELECT er FROM EvaluationResult er WHERE er.site.id = :siteId ORDER BY er.createdAt DESC")
    List<EvaluationResult> findBySiteIdOrderByCreatedAtDesc(@Param("siteId") Long siteId);
    
    /**
     * Lấy kết quả theo config và batch
     */
    @Query("SELECT er FROM EvaluationResult er WHERE er.config.id = :configId AND er.batchId = :batchId ORDER BY er.rankPosition ASC")
    List<EvaluationResult> findByConfigIdAndBatchId(@Param("configId") Long configId, @Param("batchId") String batchId);
}
