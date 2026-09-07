using UnityEngine;

/// <summary>
/// Zone de fin de niveau (Collider2D en Trigger). Quand le joueur y entre,
/// charge la scène suivante via le GameManager.
/// </summary>
[RequireComponent(typeof(Collider2D))]
public class LevelExitTrigger : MonoBehaviour
{
    [SerializeField] private string nextSceneName = "Level02";
    [SerializeField] private string targetTag = "Player";

    private void Reset()
    {
        GetComponent<Collider2D>().isTrigger = true;
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (!other.CompareTag(targetTag)) return;
        if (string.IsNullOrEmpty(nextSceneName)) return;

        if (GameManager.Instance != null)
        {
            GameManager.Instance.LoadLevel(nextSceneName);
        }
    }
}
