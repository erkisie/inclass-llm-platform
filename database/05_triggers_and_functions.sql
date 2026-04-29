
ALTER TABLE enrollments 
ADD COLUMN IF NOT EXISTS total_score NUMERIC(5,2) DEFAULT 0.00;

CREATE OR REPLACE FUNCTION calculate_total_course_score()
RETURNS TRIGGER AS $$
BEGIN
  
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE enrollments
        SET total_score = (
            SELECT COALESCE(SUM(score), 0)
            FROM scores
            WHERE student_email = NEW.student_email 
              AND course_id = NEW.course_id
        )
        WHERE student_email = NEW.student_email 
          AND course_id = NEW.course_id;
        RETURN NEW;
        

    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE enrollments
        SET total_score = (
            SELECT COALESCE(SUM(score), 0)
            FROM scores
            WHERE student_email = OLD.student_email 
              AND course_id = OLD.course_id
        )
        WHERE student_email = OLD.student_email 
          AND course_id = OLD.course_id;
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS update_student_total_score_trigger ON scores;


CREATE TRIGGER update_student_total_score_trigger
AFTER INSERT OR UPDATE OR DELETE ON scores
FOR EACH ROW
EXECUTE FUNCTION calculate_total_course_score();



UPDATE enrollments e
SET total_score = (
    SELECT COALESCE(SUM(score), 0)
    FROM scores s
    WHERE s.student_email = e.student_email 
      AND s.course_id = e.course_id
);