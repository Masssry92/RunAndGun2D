using UnityEngine;

/// <summary>
/// Système de tir multidirectionnel du joueur.
/// Direction visée : flèches directionnelles (haut/bas/gauche/droite, diagonales possibles
/// en combinant deux touches). Si aucune flèche n'est appuyée, le tir part dans la direction
/// où le personnage regarde. Tir : Ctrl gauche ou clic gauche de la souris.
/// </summary>
public class PlayerShooting : MonoBehaviour
{
    [Header("Tir")]
    [SerializeField] private Projectile projectilePrefab;
    [SerializeField] private Transform firePoint;
    [SerializeField] private float fireRate = 5f; // tirs par seconde
    [SerializeField] private float projectileSpeed = 12f;

    [Header("Munitions (bonus)")]
    [SerializeField] private bool useAmmo = false;
    [SerializeField] private int maxAmmo = 30;
    public int CurrentAmmo { get; private set; }

    [Header("Références (optionnelles)")]
    [SerializeField] private PlayerController playerController;
    [SerializeField] private Animator animator;

    private float nextFireTime;
    private Vector2 lastAimDirection = Vector2.right;

    private void Awake()
    {
        CurrentAmmo = maxAmmo;
        if (!playerController) playerController = GetComponent<PlayerController>();
        if (!animator) animator = GetComponentInChildren<Animator>();
    }

    private void Update()
    {
        Vector2 aim = ReadAimInput();
        if (aim != Vector2.zero)
        {
            lastAimDirection = aim.normalized;
        }
        else if (playerController)
        {
            lastAimDirection = playerController.FacingRight ? Vector2.right : Vector2.left;
        }

        bool wantsToFire = Input.GetKey(KeyCode.LeftControl) || Input.GetMouseButton(0);
        if (wantsToFire && Time.time >= nextFireTime)
        {
            TryFire();
        }
    }

    private Vector2 ReadAimInput()
    {
        Vector2 dir = Vector2.zero;
        if (Input.GetKey(KeyCode.UpArrow)) dir += Vector2.up;
        if (Input.GetKey(KeyCode.DownArrow)) dir += Vector2.down;
        if (Input.GetKey(KeyCode.LeftArrow)) dir += Vector2.left;
        if (Input.GetKey(KeyCode.RightArrow)) dir += Vector2.right;
        return dir;
    }

    private void TryFire()
    {
        if (useAmmo)
        {
            if (CurrentAmmo <= 0) return;
            CurrentAmmo--;
        }

        nextFireTime = Time.time + 1f / Mathf.Max(0.01f, fireRate);

        if (projectilePrefab && firePoint)
        {
            Projectile p = Instantiate(projectilePrefab, firePoint.position, Quaternion.identity);
            p.Launch(lastAimDirection, projectileSpeed, Team.Player);
        }

        if (animator && animator.runtimeAnimatorController != null) animator.SetTrigger("Shoot");
    }

    public void RefillAmmo(int amount)
    {
        CurrentAmmo = Mathf.Min(maxAmmo, CurrentAmmo + amount);
    }
}
