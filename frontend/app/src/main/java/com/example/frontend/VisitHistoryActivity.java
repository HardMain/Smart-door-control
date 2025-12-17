package com.example.frontend;

import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

public class VisitHistoryActivity extends AppCompatActivity {
    private RecyclerView recyclerView;
    private VisitAdapter adapter;
    private ProgressBar loadingProgress;
    private TextView errorText;
    private ApiService apiService;

    private static final int PAGE_SIZE = 20;
    private int currentOffset = 0;
    private boolean isLoading = false;
    private boolean hasMoreData = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_visit_history);

        recyclerView = findViewById(R.id.visitsRecyclerView);
        loadingProgress = findViewById(R.id.loadingProgress);
        errorText = findViewById(R.id.errorText);

        apiService = new ApiService();
        adapter = new VisitAdapter(this);

        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        recyclerView.setLayoutManager(layoutManager);
        recyclerView.setAdapter(adapter);

        recyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrolled(@NonNull RecyclerView recyclerView, int dx, int dy) {
                super.onScrolled(recyclerView, dx, dy);

                LinearLayoutManager layoutManager = (LinearLayoutManager) recyclerView.getLayoutManager();
                if (layoutManager == null) return;

                int visibleItemCount = layoutManager.getChildCount();
                int totalItemCount = layoutManager.getItemCount();
                int firstVisibleItemPosition = layoutManager.findFirstVisibleItemPosition();

                if (!isLoading && hasMoreData) {
                    if ((visibleItemCount + firstVisibleItemPosition) >= totalItemCount - 5
                            && firstVisibleItemPosition >= 0) {
                        loadMoreVisits();
                    }
                }
            }
        });

        loadVisits();
    }

    private void loadVisits() {
        isLoading = true;
        loadingProgress.setVisibility(View.VISIBLE);
        errorText.setVisibility(View.GONE);

        apiService.getVisitHistory(PAGE_SIZE, currentOffset, new ApiService.ApiCallback<List<Visit>>() {
            @Override
            public void onSuccess(List<Visit> visits) {
                loadingProgress.setVisibility(View.GONE);
                isLoading = false;

                if (visits.isEmpty()) {
                    if (currentOffset == 0) {
                        errorText.setText("Нет визитов");
                        errorText.setVisibility(View.VISIBLE);
                    }
                    hasMoreData = false;
                } else {
                    adapter.addVisits(visits);
                    currentOffset += visits.size();

                    if (visits.size() < PAGE_SIZE) {
                        hasMoreData = false;
                    }
                }
            }

            @Override
            public void onError(String error) {
                loadingProgress.setVisibility(View.GONE);
                isLoading = false;

                if (currentOffset == 0) {
                    errorText.setText("Ошибка загрузки: " + error);
                    errorText.setVisibility(View.VISIBLE);
                } else {
                    Toast.makeText(VisitHistoryActivity.this,
                            "Ошибка загрузки: " + error, Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void loadMoreVisits() {
        loadVisits();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (apiService != null) {
            apiService.shutdown();
        }
    }
}