using UnityEngine;

/// <summary>
/// Projectile générique utilisé aussi bien par le joueur que par les ennemis.
/// La direction est normalisée (Vector2.normalized) et la vitesse est appliquée
/// via Rigidbody2D. L'orientation visuelle (rotation du sprite) suit la trajectoire.
/// </summary>
[RequireComponent(typeof(Rigidbody2D))]
public class Projectile : MonoBehaviour
{
    [Header("Paramètres")]
    [SerializeField] private int damage = 1;
    [SerializeField] private float lifeTime = 3f;

    [Header("Collision avec le décor")]
    [Tooltip("Layers considérés comme des obstacles (sol, murs). Par défaut : tout.")]
    [SerializeField] private LayerMask obstacleMask = ~0; // ~0 = Everything

    private Rigidbody2D rb;
    private Team team;
    private bool launched;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        rb.gravityScale = 0f;
    }

    /// <summary>Lance le projectile dans une direction donnée, à une vitesse donnée, pour un camp donné.</summary>
    public void Launch(Vector2 direction, float speed, Team firingTeam)
    {
        team = firingTeam;
        launched = true;

        Vector2 dir = direction.sqrMagnitude > 0.0001f ? direction.normalized : Vector2.right;
        rb.linearVelocity = dir * speed;

        float angle = Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg;
        transform.rotation = Quaternion.Euler(0f, 0f, angle);

        Destroy(gameObject, lifeTime);
    }

    private void OnTriggerEnter2D(Collider2D other) => HandleHit(other);
    private void OnCollisionEnter2D(Collision2D collision) => HandleHit(collision.collider);

    private void HandleHit(Collider2D other)
    {
        if (!launched) return;

        string targetTag = team == Team.Player ? "Enemy" : "Player";

        if (other.CompareTag(targetTag))
        {
            if (other.TryGetComponent(out Health health))
            {
                health.TakeDamage(damage);
            }
            Destroy(gameObject);
            return;
        }

        // Touche le décor (sol / mur) -> le projectile disparaît.
        if (((1 << other.gameObject.layer) & obstacleMask) != 0 && other.CompareTag("Ground"))
        {
            Destroy(gameObject);
        }
    }
}
