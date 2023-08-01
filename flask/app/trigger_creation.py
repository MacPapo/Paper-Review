from sqlalchemy import  event , DDL
from app import db

# Trigger to check if the reviewer is a researcher of the same project
reviewer_not_project_researcher= DDL("""
CREATE OR REPLACE FUNCTION reviewer_not_project_researcher()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS(SELECT * FROM public.project pr
              WHERE pr.pid = NEW.pid AND
              pr.rsid = NEW.rvid)
    THEN RAISE EXCEPTION 'Reviewer cannot be a researcher of the same project';
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER reviewer_not_project_researcher
BEFORE INSERT OR UPDATE ON report
FOR EACH ROW
EXECUTE FUNCTION reviewer_not_project_researcher();

CREATE OR REPLACE TRIGGER reviewer_not_project_researcher_draft
BEFORE INSERT OR UPDATE ON reportdraft
FOR EACH ROW
EXECUTE FUNCTION reviewer_not_project_researcher();
""")



comment_date_check = DDL("""
CREATE OR REPLACE FUNCTION comment_date_check()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS(SELECT * FROM public.comment cm
              WHERE NEW.version_ref < cm.version_ref)
    THEN RAISE EXCEPTION 'New comment cannot be of an older version of the project';
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER comment_date_check
BEFORE INSERT OR UPDATE ON comment
FOR EACH ROW
EXECUTE FUNCTION comment_date_check();


CREATE OR REPLACE FUNCTION report_comment_date_check()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS(SELECT * FROM reportcomment rc
              WHERE NEW.version_ref < rc.version_ref)
    THEN RAISE EXCEPTION 'New reportcomment cannot be of an older version of the project';
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER report_comment_date_check
BEFORE INSERT OR UPDATE ON reportcomment
FOR EACH ROW
EXECUTE FUNCTION report_comment_date_check();

""")

no_self_report_reference = DDL("""
CREATE OR REPLACE FUNCTION check_report_not_reference_itself()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.reference IS NOT NULL AND NEW.reference = NEW.rid THEN
        RAISE EXCEPTION 'Report cannot reference itself';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER check_report_not_reference_itself_trigger
BEFORE INSERT ON report
FOR EACH ROW
EXECUTE FUNCTION check_report_not_reference_itself();

CREATE OR REPLACE TRIGGER check_reportdraft_not_reference_itself_trigger
BEFORE INSERT ON reportdraft
FOR EACH ROW
EXECUTE FUNCTION check_report_not_reference_itself();

""")

project_status_check = DDL("""
CREATE OR REPLACE FUNCTION project_status_check()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS(SELECT * FROM public.version vs
                WHERE vs.pid = NEW.pid AND (vs.project_status='Approved' OR vs.project_status='Rejected'))
    THEN RAISE EXCEPTION 'Project cannot be updated after it is approved or rejected';
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER project_status_check
BEFORE INSERT OR UPDATE ON version
FOR EACH ROW
EXECUTE FUNCTION project_status_check();


CREATE OR REPLACE TRIGGER project_draft_status_check
BEFORE INSERT OR UPDATE ON reportdraft
FOR EACH ROW
EXECUTE FUNCTION project_status_check();
""")

def create_triggers():
    with db.engine.connect() as con:
        # Execute the DDL statements directly to create triggers
        con.execute(reviewer_not_project_researcher)
        con.execute(comment_date_check)
        con.execute(no_self_report_reference)
        con.execute(project_status_check)

        # Commit the changes to the database
        con.commit()
