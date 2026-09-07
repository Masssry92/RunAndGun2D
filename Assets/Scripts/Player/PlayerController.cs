using UnityEngine;

/// <summary>
/// Déplacement, saut et orientation du personnage principal.
/// Contrôles : Q/D (ou A/D) pour se déplacer, Espace ou W pour sauter.
/// </summary>
[RequireComponent(typeof(Rigidbody2D))]
public class PlayerController : MonoBehaviour
{
    [Header("Déplacement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 9f;

    [Header("Détection du sol")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private float groundCheckRadius = 0.18f;
    [SerializeField] private LayerMask groundLayer = ~0; // ~0 = Everything par défaut

    [Header("Références (optionnelles)")]
    [SerializeField] private Animator animator;
    [SerializeField] private SpriteRenderer spriteRenderer;

    public bool IsGrounded { get; private set; }
    public bool FacingRight { get; private set; } = true;
    public Vector2 MoveInput { get; private set; }

    private Rigidbody2D rb;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        if (!animator) animator = GetComponentInChildren<Animator>();
        if (!spriteRenderer) spriteRenderer = GetComponentInChildren<SpriteRenderer>();
    }

    private void Update()
    {
        float h = 0f;
        if (Input.GetKey(KeyCode.A)) h = -1f;
        if (Input.GetKey(KeyCode.D)) h = 1f;

        MoveInput = new Vector2(h, 0f);

        if (h > 0.01f) SetFacing(true);
        else if (h < -0.01f) SetFacing(false);

        bool jumpPressed = Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.Space);
        if (jumpPressed && IsGrounded)
        {
            rb.linearVelocity = new Vector2(rb.linearVelocity.x, jumpForce);
            if (animator && animator.runtimeAnimatorController != null) animator.SetTrigger("Jump");
        }

        if (animator && animator.runtimeAnimatorController != null)
        {
            animator.SetFloat("Speed", Mathf.Abs(rb.linearVelocity.x));
            animator.SetBool("Grounded", IsGrounded);
            animator.SetFloat("VerticalVelocity", rb.linearVelocity.y);
        }
    }

    private void FixedUpdate()
    {
        rb.linearVelocity = new Vector2(MoveInput.x * moveSpeed, rb.linearVelocity.y);
        IsGrounded = groundCheck != null &&
                     Physics2D.OverlapCircle(groundCheck.position, groundCheckRadius, groundLayer);
    }

    private void SetFacing(bool right)
    {
        FacingRight = right;
        if (spriteRenderer) spriteRenderer.flipX = !right;
    }

    private void OnDrawGizmosSelected()
    {
        if (!groundCheck) return;
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(groundCheck.position, groundCheckRadius);
    }
}
