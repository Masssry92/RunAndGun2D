using UnityEngine;

/// <summary>
/// Ennemi à distance : détecte le joueur dans sa zone d'attaque et tire des
/// projectiles dans sa direction à un rythme régulier.
/// </summary>
public class EnemyRanged : EnemyBase
{
    [Header("Tir")]
    [SerializeField] private Projectile projectilePrefab;
    [SerializeField] private Transform firePoint;
    [SerializeField] private float fireRate = 1f;
    [SerializeField] private float projectileSpeed = 8f;

    [Header("Références (optionnelles)")]
    [SerializeField] private SpriteRenderer spriteRenderer;
    [SerializeField] private Animator animator;

    private float nextFireTime;

    protected override void Awake()
    {
        base.Awake();
        if (!spriteRenderer) spriteRenderer = GetComponentInChildren<SpriteRenderer>();
        if (!animator) animator = GetComponentInChildren<Animator>();
    }

    private void Update()
    {
        if (health.IsDead || target == null) return;

        bool facingRight = target.position.x >= transform.position.x;
        if (spriteRenderer) spriteRenderer.flipX = !facingRight;

        if (Time.time >= nextFireTime)
        {
            Fire();
        }
    }

    private void Fire()
    {
        nextFireTime = Time.time + 1f / Mathf.Max(0.01f, fireRate);

        if (!projectilePrefab || !firePoint || target == null) return;

        Vector2 direction = (Vector2)target.position - (Vector2)firePoint.position;
        Projectile p = Instantiate(projectilePrefab, firePoint.position, Quaternion.identity);
        p.Launch(direction, projectileSpeed, Team.Enemy);

        if (animator && animator.runtimeAnimatorController != null) animator.SetTrigger("Shoot");
    }
}
