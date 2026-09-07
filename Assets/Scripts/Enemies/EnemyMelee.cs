using UnityEngine;

/// <summary>
/// Ennemi de mêlée : détecte le joueur dans sa zone, se rapproche, puis attaque
/// au contact / à courte portée.
/// </summary>
public class EnemyMelee : EnemyBase
{
    [Header("Comportement")]
    [SerializeField] private float moveSpeed = 2f;
    [SerializeField] private float attackRange = 1f;
    [SerializeField] private float attackCooldown = 1f;
    [SerializeField] private int attackDamage = 1;

    [Header("Références (optionnelles)")]
    [SerializeField] private Rigidbody2D rb;
    [SerializeField] private SpriteRenderer spriteRenderer;
    [SerializeField] private Animator animator;

    private float nextAttackTime;

    protected override void Awake()
    {
        base.Awake();
        if (!rb) rb = GetComponent<Rigidbody2D>();
        if (!spriteRenderer) spriteRenderer = GetComponentInChildren<SpriteRenderer>();
        if (!animator) animator = GetComponentInChildren<Animator>();
    }

    private void FixedUpdate()
    {
        if (health.IsDead || rb == null) return;

        if (target == null)
        {
            rb.linearVelocity = new Vector2(0f, rb.linearVelocity.y);
            SetAnimSpeed(0f);
            return;
        }

        float distance = Vector2.Distance(target.position, transform.position);
        bool facingRight = target.position.x >= transform.position.x;
        if (spriteRenderer) spriteRenderer.flipX = !facingRight;

        if (distance > attackRange)
        {
            float dir = Mathf.Sign(target.position.x - transform.position.x);
            rb.linearVelocity = new Vector2(dir * moveSpeed, rb.linearVelocity.y);
            SetAnimSpeed(moveSpeed);
        }
        else
        {
            rb.linearVelocity = new Vector2(0f, rb.linearVelocity.y);
            SetAnimSpeed(0f);
            TryAttack();
        }
    }

    private void TryAttack()
    {
        if (Time.time < nextAttackTime) return;
        nextAttackTime = Time.time + attackCooldown;

        if (animator && animator.runtimeAnimatorController != null) animator.SetTrigger("Attack");

        if (target != null && target.TryGetComponent(out Health targetHealth))
        {
            targetHealth.TakeDamage(attackDamage);
        }
    }

    private void SetAnimSpeed(float speed)
    {
        if (animator && animator.runtimeAnimatorController != null) animator.SetFloat("Speed", speed);
    }
}
