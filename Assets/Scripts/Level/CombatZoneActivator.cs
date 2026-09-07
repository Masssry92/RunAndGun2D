using UnityEngine;

/// <summary>
/// Zone en Trigger qui active un groupe d'ennemis (ou une zone de combat) lorsque
/// le joueur y pénètre, sans collision physique directe.
/// </summary>
[RequireComponent(typeof(Collider2D))]
public class CombatZoneActivator : MonoBehaviour
{
    [SerializeField] private string targetTag = "Player";
    [SerializeField] private GameObject[] enemiesToActivate;
    [SerializeField] private bool activateOnce = true;

    private bool triggered;

    private void Reset()
    {
        GetComponent<Collider2D>().isTrigger = true;
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (triggered && activateOnce) return;
        if (!other.CompareTag(targetTag)) return;

        foreach (var enemy in enemiesToActivate)
        {
            if (enemy) enemy.SetActive(true);
        }
        triggered = true;
    }
}
