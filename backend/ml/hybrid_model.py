from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer


from backend.ml.ast_features import transform_ast_features

def create_tfidf_vectorizer():
    tfidf_vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(2, 5),
        lowercase=False
    )
    return tfidf_vectorizer

def create_ast_transformer():
    return FunctionTransformer(transform_ast_features, validate=False)

def create_classifier():
    return LogisticRegression(
        max_iter=10000,
        class_weight='balanced',
        random_state=42
    )

def create_models():
    tfidf_model=Pipeline([
        ("features",create_tfidf_vectorizer()),
        ("classifier", create_classifier())
    ])
    ast_model=Pipeline([
        ("features", create_ast_transformer()),
        ("classifier", create_classifier())
    ])

    hybrid_model=Pipeline([
        ("features", FeatureUnion([
            ("tfidf",create_tfidf_vectorizer()),
            ("ast",create_ast_transformer())
        ])),
        ("classifier", create_classifier())
    ])

    return {
        "tfidf": tfidf_model,
        "ast": ast_model,
        "hybrid": hybrid_model
    }
