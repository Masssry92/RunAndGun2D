using UnityEngine;

/// <summary>
/// Classe de base abstraite pour tous les ennemis : gère la vie, la détection du joueur
/// et la mort. EnemyMelee et EnemyRanged en héritent et n'implémentent que leur
/// comportement spécifique (héritage + polymorphisme).
/// </summary>
[RequireComponent(typeof(Health))]
public abstract class EnemyBase : MonoBehaviour
{
    [Header("Détection")]
    [SerializeField] protected DetectionZone detectionZone;

    [Header("Récompense (bonus score)")]
    [SerializeField] protected int scoreValue = 10;

    protected Health health;
    protected Transform target;

    protected virtual void Awake()
    {
        health = GetComponent<Health>();
        health.OnDeath.AddListener(HandleDeath);

        if (detectionZone)
        {
            detectionZone.OnTargetEnter.AddListener(OnTargetDetected);
            detectionZone.OnTargetExit.AddListener(OnTargetLost);
        }
    }

    protected virtual void OnTargetDetected(Transform detected) => target = detected;

    protected virtual void OnTargetLost() => target = null;

    protected virtual void HandleDeath()
    {
        enabled = false;
        foreach (var col in GetComponents<Collider2D>())
        {
            col.enabled = false;
        }

        if (ScoreManager.Instance != null)
        {
            ScoreManager.Instance.AddScore(scoreValue);
        }

        Destroy(gameObject, 1.5f);
    }
}
