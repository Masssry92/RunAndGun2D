using UnityEngine;
using UnityEngine.Events;

/// <summary>Score simple (bonus). Singleton persistant entre les scènes.</summary>
public class ScoreManager : MonoBehaviour
{
    public static ScoreManager Instance { get; private set; }

    [SerializeField] private int score;
    public UnityEvent<int> OnScoreChanged;

    public int Score => score;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    public void AddScore(int amount)
    {
        score += amount;
        OnScoreChanged?.Invoke(score);
    }
}
