from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def match_resume(resume_text, job_description):
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding).item()
    return round(similarity_score * 100, 2)
