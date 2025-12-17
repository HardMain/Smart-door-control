package com.example.frontend;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class VisitAdapter extends RecyclerView.Adapter<VisitAdapter.VisitViewHolder> {

    private List<Visit> visits = new ArrayList<>();
    private final Context context;

    public VisitAdapter(Context context) {
        this.context = context;
    }

    @NonNull
    @Override
    public VisitViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.visit_item, parent, false);
        return new VisitViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull VisitViewHolder holder, int position) {
        Visit visit = visits.get(position);
        holder.bind(visit);
    }

    @Override
    public int getItemCount() {
        return visits.size();
    }

    public void addVisits(List<Visit> newVisits) {
        int startPosition = visits.size();
        visits.addAll(newVisits);
        notifyItemRangeInserted(startPosition, newVisits.size());
    }

    public void clearVisits() {
        visits.clear();
        notifyDataSetChanged();
    }

    class VisitViewHolder extends RecyclerView.ViewHolder {
        private final ImageView photoImageView;
        private final TextView timestampTextView;
        private final TextView idTextView;

        public VisitViewHolder(@NonNull View itemView) {
            super(itemView);
            photoImageView = itemView.findViewById(R.id.visitPhoto);
            timestampTextView = itemView.findViewById(R.id.visitTimestamp);
            idTextView = itemView.findViewById(R.id.visitId);
        }

        public void bind(Visit visit) {
            try {
                SimpleDateFormat inputFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
                SimpleDateFormat outputFormat = new SimpleDateFormat("dd.MM.yyyy HH:mm:ss", Locale.getDefault());
                Date date = inputFormat.parse(visit.getTimestamp());
                if (date != null) {
                    timestampTextView.setText(outputFormat.format(date));
                } else {
                    timestampTextView.setText(visit.getTimestamp());
                }
            } catch (Exception e) {
                timestampTextView.setText(visit.getTimestamp());
            }

            idTextView.setText("ID: " + visit.getId());

            String photoUrl = visit.getPhotoUrl();
            if (photoUrl != null && !photoUrl.isEmpty()) {
                if (photoUrl.startsWith("/")) {
                    photoUrl = ApiService.BASE_URL + photoUrl;
                }

                Glide.with(context)
                        .load(photoUrl)
                        .placeholder(android.R.drawable.ic_menu_camera)
                        .error(android.R.drawable.ic_menu_report_image)
                        .centerCrop()
                        .into(photoImageView);
            }
        }
    }
}
