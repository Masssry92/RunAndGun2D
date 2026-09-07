using UnityEngine;
using UnityEngine.Events;

/// <summary>
/// Zone de détection basée sur un Collider2D configuré en Trigger.
/// Utilisée par les ennemis pour repérer le joueur sans collision physique directe
/// (voir consigne §4 : distinguer Collision physique et zone logique en Trigger).
/// </summary>
[RequireComponent(typeof(Collider2D))]
public class DetectionZone : MonoBehaviour
{
    [SerializeField] private string targetTag = "Player";

    public UnityEvent<Transform> OnTargetEnter;
    public UnityEvent OnTargetExit;

    public bool HasTarget { get; private set; }
    public Transform CurrentTarget { get; private set; }

    private void Reset()
    {
        GetComponent<Collider2D>().isTrigger = true;
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (!other.CompareTag(targetTag)) return;
        HasTarget = true;
        CurrentTarget = other.transform;
        OnTargetEnter?.Invoke(CurrentTarget);
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        if (!other.CompareTag(targetTag)) return;
        HasTarget = false;
        CurrentTarget = null;
        OnTargetExit?.Invoke();
    }
}
